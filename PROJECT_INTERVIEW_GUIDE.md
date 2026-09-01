# Finance 项目深度学习与面试指南

> 最后核对日期：2026-09-01  
> 文档目标：如实记录当前代码已经实现的能力、存在的问题、调用链和重构路线，供项目维护、学习复盘与面试准备使用。  
> 重要原则：本文把“当前已实现”和“未来计划”严格分开。未落地的功能不能在简历或面试中描述为已完成。

---

## 1. 项目当前的真实定位

Finance 当前是一个课程项目性质的金融产品信息与行情展示系统，主要能力包括：

- 用户注册、登录和基础用户 CRUD。
- 股票基础信息条件查询。
- 基金产品条件查询。
- 用户收藏和取消收藏股票、基金。
- 使用 ECharts 展示股票 K 线。
- 使用 ECharts 展示基金单位净值、日增长率和稀疏的累计收益率数据。
- 使用独立 Flask 服务调用 AkShare，并完成 DataFrame 清洗和 JSON 转换。

当前更准确的项目名称是：

> 金融产品信息与行情分析系统

当前还不能严谨地称为完整的“个人投资理财平台”，因为下面这些能力尚未实现：

- JWT 或 Session 登录态。
- Spring Security 鉴权。
- 用户角色和 RBAC 权限模型。
- 风险测评问卷与评分。
- 投资组合、持仓和交易记录。
- 持仓成本、当前市值和组合收益计算。
- 收入、支出和账单分类。
- 财务目标和预算。
- Redis 行情缓存。
- Agent、Tool Calling、RAG 或 MCP Server。
- Docker Compose 部署。

---

## 2. 当前技术栈

| 层次 | 当前技术 | 说明 |
|---|---|---|
| 前端 | Vue 3.2、Vue Router 4 | Options API 与 Composition API 混用 |
| UI | Element Plus 2.10 | 页面表格、表单、导航与消息提示 |
| 图表 | ECharts 5.6 | 股票 K 线、基金净值走势 |
| HTTP | Axios 1.10 | 前端请求 Spring Boot 和 Flask |
| Java | Java 21 | `pom.xml` 编译目标为 Java 21 |
| Java Web | Spring Boot 3.4.1 | 当前主要业务后端 |
| ORM | MyBatis 3 + MyBatis-Plus | 两套依赖混用，需要后续统一 |
| 数据库 | MySQL 8 | 用户、股票、基金和收藏数据 |
| Python Web | Flask 3.1.3 | 独立行情数据服务 |
| 行情数据 | AkShare 1.18.94 | 对接东方财富等公开数据源 |
| 数据处理 | Pandas 2.3.3 | DataFrame 字段选择、日期处理和合并 |
| Python 测试 | pytest 9.1.1 | 当前共有 10 个测试 |

### 2.1 不应当为了简历而声称使用的依赖

Java `pom.xml` 中存在 Redis、Jython、Fastjson、华为 DWS JDBC、Jeval 等依赖，但“依赖出现在 `pom.xml`”不等于“项目实际使用了该技术”。

面试时只有满足下面条件才应描述为已使用：

1. 代码中存在真实业务调用。
2. 能解释使用场景和替代方案。
3. 有运行验证或测试。
4. 能说明失败场景及处理方式。

例如，当前不能说“使用 Redis 缓存行情”，因为还没有对应缓存代码、缓存 Key、TTL 或一致性策略。

---

## 3. 当前项目目录

```text
Finance/
├── backend/                     Spring Boot 业务后端
│   ├── pom.xml
│   └── src/main/
│       ├── java/cn/edu/lut/
│       │   ├── config/
│       │   ├── controller/
│       │   ├── entity/
│       │   ├── handler/
│       │   ├── mapper/
│       │   ├── pythonpart/
│       │   ├── service/
│       │   └── service/impl/
│       └── resources/
│           ├── application.yml
│           └── mapper/
├── frontend/                    Vue 3 前端
│   ├── package.json
│   └── src/
│       ├── pages/
│       ├── router/
│       ├── App.vue
│       └── main.js
├── market-service/              Flask + AkShare 行情服务
│   ├── app/
│   │   ├── clients/
│   │   ├── errors/
│   │   ├── routes/
│   │   └── services/
│   ├── tests/
│   ├── requirements.txt
│   ├── README.md
│   └── run.py
└── PROJECT_INTERVIEW_GUIDE.md   本文档
```

本仓库根目录中同学的 `springbootm47gb` 不属于当前 Finance 项目。当前整理没有合并同学的代码。

---

## 4. 当前真实架构

当前并不是“Vue 只调用 Spring Boot”的统一入口架构，而是两条请求链并存：

```text
链路 A：业务数据

Vue
  └── Axios → Spring Boot :81
                    └── MyBatis → MySQL/finance

链路 B：行情图表

Vue
  └── Axios → Flask :5000
                    └── AkShare → 外部公开行情数据源
```

此外，Java 后端还残留一条旧路径：

```text
FinanceProductController
  └── PythonExecutor
        └── ProcessBuilder 启动本机 Python 脚本
```

该路径使用硬编码的 Python 解释器和脚本路径，对应脚本不在当前项目内，属于应当移除的遗留设计。

### 4.1 计划中的目标架构

下面是未来计划，不是当前实现：

```text
Vue
  └── Spring Boot
        ├── MySQL
        ├── Redis（未来）
        ├── Flask Market Service → AkShare
        └── Agent（未来）→ LLM API

外部 MCP Client（未来）
  └── MCP Server → Spring Boot 受控 API
```

目标是让 Vue 只访问 Spring Boot，统一鉴权、错误响应、日志和用户身份。

---

## 5. 前端模块

### 5.1 页面和路由

| 路由 | 页面 | 当前作用 |
|---|---|---|
| `/` | `LoginPage.vue` | 登录 |
| `/register` | `RegisterPage.vue` | 注册 |
| `/main` | `MainPage.vue` | 主框架和侧边导航 |
| `/user/list` | `UserList.vue` | 用户列表、编辑和删除 |
| `/user/add` | `AddUser.vue` | 新增用户 |
| `/financeproduct/list` | `ProductList.vue` | 基金查询和收藏 |
| `/financeproduct/favor` | `FundFavor.vue` | 基金收藏列表 |
| `/financeproduct/chart` | `FundChart.vue` | 基金净值走势 |
| `/stock/list` | `StockList.vue` | 股票查询和收藏 |
| `/stock/favor` | `StockFavor.vue` | 股票收藏列表 |
| `/stock/kline` | `KLineChart.vue` | 股票 K 线 |

### 5.2 当前 Axios 地址

普通业务接口通过 `frontend/src/main.js` 中的配置访问：

```text
http://localhost:81
```

K 线和基金图表页面则硬编码访问：

```text
http://localhost:5000/api/kline
http://localhost:5000/api/fundchart
```

这是当前架构需要重构的原因之一。

### 5.3 前端当前的安全问题

登录页面在选择“记住密码”时会把用户名和明文密码写入 `localStorage`：

```text
username
password
rememberPassword
```

登录成功后还会把包含用户字段的对象写入：

```text
user
```

问题包括：

- XSS 发生时，脚本可以读取 `localStorage`。
- 明文密码长期保存在浏览器中。
- 前端保存的 `userId` 可以被用户修改。
- 后端收藏接口相信请求中的 `userId`，可能产生越权。
- 用户列表页面直接展示密码字段。

正确方向是：

- 服务端使用 BCrypt 存储密码散列。
- 登录成功返回短期 Access Token。
- 前端不保存明文密码。
- 后端从认证上下文获取用户 ID。
- 用户 DTO 永远不返回密码字段。

### 5.4 已确认的接口路径问题

当前注册页面调用：

```text
POST /users/register
```

Java 后端实际提供：

```text
POST /register
```

这是一个真实的不一致，需要后续修复并增加测试。

---

## 6. Spring Boot 后端模块

### 6.1 分层结构

当前主要采用：

```text
Controller
  → Service Interface
    → ServiceImpl
      → Mapper Interface
        → Mapper XML
          → MySQL
```

各层当前职责：

- Controller：接收 JSON 请求，调用 Service，包装 `Result`。
- Service：业务方法接口。
- ServiceImpl：校验少量业务参数并调用 Mapper。
- Mapper：声明数据库操作。
- Mapper XML：编写 SQL、动态条件和关联查询。
- Entity/DTO/VO：承载请求、数据库记录或组合查询结果。

### 6.2 用户接口

| 方法 | 路径 | 作用 | 当前问题 |
|---|---|---|---|
| POST | `/login` | 用户名密码登录 | 明文比较，无 Token |
| POST | `/register` | 注册 | 只写用户名和密码 |
| POST | `/user/list` | 用户列表 | 无鉴权，可能返回密码 |
| POST | `/user/edit` | 编辑用户 | 无鉴权和字段权限控制 |
| POST | `/user/delete` | 删除用户 | 无鉴权，使用请求 ID |

登录的真实流程：

```text
LoginPage.vue
  → POST /login
    → UserController.login
      → UserServiceImpl.login
        → UserMapper.selectByUsername
          → SELECT * FROM users WHERE username = ?
      → Java 使用 equals 比较明文密码
      → 返回完整 User 对象
  → 前端写入 localStorage
```

该流程能演示基本分层，但不能作为生产级认证方案。

### 6.3 股票接口

| 方法 | 路径 | 作用 |
|---|---|---|
| POST | `/stock/list` | 条件查询股票并返回收藏状态 |
| POST | `/stock/favor` | 查询用户收藏股票 |
| POST | `/stock/favorite` | 添加收藏 |
| POST | `/stock/unfavorite` | 取消收藏 |

股票条件包括：

- 股票代码 `code`
- 股票名称 `name`
- 行业 `industry`
- 用户 ID `userId`

股票列表关联逻辑：

```sql
stock_info si
LEFT JOIN stock_favorite sf
  ON si.code = sf.stock_code
 AND sf.user_id = #{userId}
```

该查询使每条股票记录可以同时返回 `isFavorite`，避免前端再逐条查询收藏状态。

### 6.4 基金接口

| 方法 | 路径 | 作用 |
|---|---|---|
| POST | `/financeproduct/list` | 条件查询基金并返回收藏状态 |
| POST | `/financeproduct/favor` | 查询用户收藏基金 |
| POST | `/financeproduct/favorite` | 添加基金收藏 |
| POST | `/financeproduct/unfavorite` | 取消基金收藏 |
| POST | `/financeproduct/detail/{symbol}` | 调用遗留 PythonExecutor |

基金条件目前只实际使用：

- 产品代码 `productCode`
- 产品名称 `productName`
- 产品类型 `productType`
- 用户 ID `userId`

虽然 `FinanceProduct` 中存在 `riskLevel`、`expectedReturn`、`minAmount` 等字段，但目前没有完整的风险测评、适配规则或高级筛选流程。

### 6.5 统一响应对象

当前 Java 使用：

```json
{
  "code": 200,
  "msg": "success",
  "data": {}
}
```

需要注意：当前很多错误仍然返回 HTTP 200，只在 JSON 的 `code` 中表达错误。这不符合标准 HTTP 语义。未来应同时使用正确 HTTP 状态码。

### 6.6 全局异常处理

`GlobalExceptionHandler` 当前处理：

- `NullPointerException`
- `ClassNotFoundException`
- `RuntimeException`

不足之处：

- 没有参数校验异常的统一结构。
- 直接返回部分异常消息，可能暴露内部信息。
- 没有 request ID。
- 没有区分客户端错误、业务错误和上游错误。
- 使用 `System.out.println`，缺少结构化日志。

---

## 7. 当前数据库模型

根据 Mapper XML，可以确认当前至少依赖以下表：

```text
users
stock_info
stock_favorite
financeproduct
fund_favorite
```

### 7.1 关系示意

```text
users
  1 ────── N stock_favorite N ────── 1 stock_info

users
  1 ────── N fund_favorite  N ────── 1 financeproduct
```

### 7.2 收藏表应具备的约束

代码使用了 MySQL `INSERT IGNORE` 防止重复收藏，但正确的前提是数据库存在唯一约束：

```text
stock_favorite(user_id, stock_code) UNIQUE
fund_favorite(user_id, fund_code) UNIQUE
```

如果没有唯一约束，`INSERT IGNORE` 不能可靠防止重复数据。

### 7.3 当前数据库工程问题

- 仓库没有可确认的 Flyway/Liquibase 迁移脚本。
- 缺少完整建库 SQL 和演示数据。
- `application.yml` 中存在明文数据库密码。
- 用户密码是明文。
- 缺少外键和索引的可审计定义。
- 删除用户时没有说明收藏记录如何处理。
- 没有事务边界设计。

面试时不要声称“通过事务保证数据一致性”，因为当前代码没有对应实现证据。

---

## 8. Python 行情服务

### 8.1 职责边界

Python 服务只负责：

- 调用 AkShare。
- 校验行情查询参数。
- 清洗 DataFrame。
- 将 NumPy/Pandas 类型转换为标准 JSON 类型。
- 统一上游异常响应。

Python 服务不负责：

- 用户登录。
- 用户收藏。
- MySQL 访问。
- 投资组合。
- 投资建议。
- Agent 或 MCP。

### 8.2 内部分层

```text
Route
  → Service
    → AkshareClient
      → AkShare
```

- `routes`：读取 HTTP 参数、执行校验、返回 JSON。
- `services`：DataFrame 清洗、转换和合并。
- `clients`：封装 AkShare 函数调用。
- `errors`：统一 400 和 502 响应。

### 8.3 Application Factory

服务使用 `create_app` 创建 Flask 实例，而不是在一个大文件中创建全局对象并放置全部逻辑。

收益包括：

- 测试时可以创建独立 Flask 实例。
- 可以注入受控的行情 Client。
- 路由可以通过 Blueprint 拆分。
- 配置可以根据环境变化。

### 8.4 当前接口

#### 健康检查

```http
GET /health
```

```json
{
  "data": {
    "service": "market-service",
    "status": "ok"
  }
}
```

健康检查只证明 Flask 进程和路由正常，不证明 AkShare 外部数据源可用。

#### 股票 K 线

```http
GET /api/kline?code=000001&start=20250801&end=20250815
```

输出数组顺序为：

```text
[date, open, close, low, high]
```

这个顺序是为了兼容现有 ECharts 页面，不是通用行业标准。

#### 基金图表

```http
GET /api/fundchart?code=110022&start=20250801&end=20250815
```

输出数组顺序为：

```text
[date, unitValue, dailyPercentage, totalReturn]
```

### 8.5 参数校验

当前校验：

- 代码必须是 6 位数字。
- 日期格式必须为 `yyyyMMdd`。
- 日期必须真实存在。
- `start` 不能晚于 `end`。
- 查询范围不能超过 10 年。

校验失败返回 HTTP 400，并且不会调用 AkShare。

### 8.6 上游异常处理

AkShare 或外部数据源失败时返回 HTTP 502：

```json
{
  "code": "MARKET_DATA_UNAVAILABLE",
  "message": "行情数据暂时不可用，请稍后重试",
  "requestId": "..."
}
```

客户端不会看到代理地址、调用栈或 AkShare 内部异常。

### 8.7 基金累计收益率为什么经常是 null

AkShare 的“单位净值走势”接近每日数据，而“累计收益率走势”是稀疏采样数据。当前实现按日期精确合并：

```text
daily net value LEFT JOIN sparse total return ON date
```

因此很多日期没有对应累计收益率，会返回 `null`。这不是 JSON 转换错误。

当前没有使用前向填充、最近邻匹配或线性插值，因为这些方法可能改变数据含义。未来更好的接口设计是返回两条独立时间序列。

### 8.8 测试状态

当前 Python 服务共有 10 个 pytest 测试，覆盖：

- 健康检查。
- K 线格式和日期排序。
- 非法代码。
- 日期倒置。
- 超过 10 年的范围。
- 空行情。
- 上游异常转 HTTP 502。
- 基金净值和收益率合并。
- `NaN` 转 `null`。
- 非法日期格式。

最近一次验证结果：

```text
10 passed
No broken requirements found.
```

还没有覆盖真实外部数据源的稳定集成测试，因为外部数据可能随网络和上游站点变化。真实接口已经进行过人工冒烟验证。

---

## 9. 关键业务调用链

### 9.1 股票列表与收藏状态

```text
StockList.vue
  → POST /stock/list
    → StockController.list
      → StockServiceImpl.getStockList
        → StockMapper.selectStockList
          → stock_info LEFT JOIN stock_favorite
      → Result.success(list)
  → Element Plus 表格展示
```

要能够解释：

- 为什么使用 `LEFT JOIN`：即使用户未收藏，也要显示全部股票。
- 为什么关联条件包含 `user_id`：收藏状态属于特定用户。
- 为什么返回 `isFavorite`：减少前端 N+1 次收藏状态查询。

### 9.2 添加股票收藏

```text
StockList.vue
  → POST /stock/favorite {userId, code}
    → StockController.addFavorite
      → StockServiceImpl.addFavorite
        → StockMapper.insertFavorite
          → INSERT IGNORE stock_favorite
```

当前问题：`userId` 来自前端请求，可以被篡改。目标实现应从 JWT 身份中获取用户 ID。

### 9.3 K 线查询

```text
KLineChart.vue
  → GET Flask /api/kline
    → stock route
      → validate_market_query
      → StockService.get_kline
        → AkshareClient.get_stock_history
          → ak.stock_zh_a_hist
      → DataFrame 字段选择、日期排序和数值转换
    → JSON data
  → ECharts candlestick
```

### 9.4 基金净值查询

```text
FundChart.vue
  → GET Flask /api/fundchart
    → fund route
      → validate_market_query
      → FundService.get_chart
        ├── AkshareClient.get_fund_values
        └── AkshareClient.get_fund_returns
      → 日期标准化
      → LEFT JOIN
      → NaN 转 null
    → JSON data
  → ECharts line series
```

---

## 10. 当前最重要的设计问题

下面按面试和安全风险排序。

### P0：认证和敏感数据

1. 密码明文存储和比较。
2. 前端把明文密码写入 `localStorage`。
3. 登录没有 JWT 或 Session。
4. 后端接口没有真正鉴权。
5. 用户列表可能返回和展示密码。
6. 收藏操作相信前端提供的 `userId`。
7. 数据库密码写入仓库配置。

### P1：服务边界

1. Vue 同时访问 Spring Boot 和 Flask。
2. Python CORS 仍需要对浏览器开放。
3. Java 中保留不可移植的 `PythonExecutor`。
4. Spring Boot 没有统一代理行情接口。
5. 外部 HTTP 调用还没有超时、重试和熔断策略。

### P1：可复现性和测试

1. 缺少数据库迁移脚本。
2. Java 后端没有可确认的业务测试。
3. Vue 没有可确认的组件测试。
4. 缺少统一根目录 README。
5. 缺少 Docker Compose。
6. 没有 CI。

### P2：代码质量和依赖

1. MyBatis 与 MyBatis-Plus 混用。
2. `pom.xml` 存在疑似无用或老旧依赖。
3. 使用 Fastjson 1.x。
4. Controller 使用字段注入而非构造器注入。
5. 存在大量注释掉的旧代码。
6. 使用 `System.out.println` 输出调试信息。
7. Java 响应错误未充分使用 HTTP 状态码。

---

## 11. 面试时现在可以怎么说

### 11.1 当前真实简历描述

#### 金融产品信息与行情分析系统｜课程项目

**Vue 3 / Element Plus / Spring Boot / MyBatis / MySQL / Flask / AkShare / ECharts**

- 基于 Vue 3 和 Spring Boot 开发前后端分离的金融产品信息系统，实现用户管理、股票与基金条件查询、自选收藏等功能。
- 使用 MyBatis 编写股票、基金与用户收藏的关联查询，根据用户 ID 返回收藏状态，完成 Java 对象、数据库字段和前端展示之间的映射。
- 将原有单文件 Flask 行情程序重构为 Application Factory、Blueprint、Service 和 Client 分层结构，对股票历史行情及基金净值数据进行参数校验、清洗和统一 JSON 转换。
- 使用 ECharts 展示股票 K 线和基金净值走势，并通过 pytest 覆盖参数错误、空数据、缺失值和上游异常等边界场景。

### 11.2 可以强调的技术点

- 动态 SQL 和收藏关联查询。
- `LEFT JOIN` 与 `INNER JOIN` 的使用场景。
- Flask Application Factory 和 Blueprint。
- 外部数据源隔离。
- DataFrame 到 JSON 的数据类型边界。
- 400、500、502 的语义区别。
- 测试中通过依赖注入替换外部行情 Client。

### 11.3 不能说的内容

| 不能声称 | 原因 |
|---|---|
| 使用 Spring Security + JWT 完成鉴权 | 尚未实现 |
| 使用 BCrypt 加密密码 | 尚未实现 |
| 实现用户风险评估 | 只有产品风险字段，没有问卷和评分 |
| 实现投资组合管理 | 没有组合、持仓和交易模型 |
| 通过 Redis 缓存行情 | 只有依赖，没有缓存代码 |
| 实现收益计算 | 仅展示 AkShare 基金累计收益率，不是持仓收益计算 |
| 实现 Agent 或 MCP | 尚未实现 |
| 使用微服务架构 | 当前只有一个 Java 后端和一个轻量 Python 数据服务 |
| 通过完整自动化测试保证系统质量 | 当前只有 Python 服务有 10 个测试 |

### 11.4 如果被问到项目不足

不要回避。可以回答：

> 这个项目最初是课程项目，第一版更关注功能跑通，因此认证、配置管理和测试不足。我重新审计后先把最独立的 Python 行情部分拆成可测试模块，下一步会让 Spring Boot 成为统一入口，然后用 Spring Security、JWT 和 BCrypt 重构用户身份，最后再添加投资组合和 Agent Tools。这个过程让我认识到“能运行”和“具备工程质量”是两个不同阶段。

这比把未实现能力包装成“已经使用”更可信。

---

## 12. 高频面试问题与回答要点

### Q1：为什么使用 Flask，而不是让 Java 直接获取行情？

回答要点：

- AkShare 是 Python 生态库。
- Python 服务负责外部数据适配，Java 负责用户和业务规则。
- HTTP 边界比每次用 `ProcessBuilder` 创建 Python 进程更稳定。
- Python 服务可以独立测试、升级和替换数据源。
- 当前前端仍直连 Flask，目标是改成 Spring Boot 统一代理。

### Q2：为什么不继续使用 ProcessBuilder？

- 每次请求创建进程开销大。
- 并发时可能产生大量 Python 进程。
- Python 和脚本路径难以跨环境配置。
- stdout 混合日志和 JSON 时容易解析失败。
- 超时、取消、进程回收更难处理。
- ProcessBuilder 更适合低频离线任务，而非实时 HTTP 查询。

### Q3：Application Factory 解决什么问题？

- 避免模块导入时就固定创建全局应用。
- 测试可以创建独立 App。
- 支持注入配置和测试替身。
- 路由、异常处理和扩展可以统一注册。

### Q4：为什么 Route、Service、Client 要分开？

- Route 只处理 HTTP。
- Service 处理数据转换和业务规则。
- Client 隔离外部 API。
- AkShare 发生变化时，尽量只修改 Client 或转换层。
- 测试可以替换 Client，不依赖真实网络。

### Q5：为什么上游失败返回 502？

- 请求已经到达 Flask。
- Flask 自身仍在运行。
- 失败来自它依赖的上游行情数据源。
- 502 比笼统 500 更能表达网关/上游失败。

### Q6：为什么空 DataFrame 返回空数组，而不是错误？

- “没有符合条件的数据”和“服务发生故障”语义不同。
- 空数据是合法结果。
- 缺少预期列或请求上游失败才属于异常。

### Q7：为什么 `NaN` 要转换成 `null`？

- Pandas/NumPy 的 `NaN` 不属于严格 JSON 标准中的数值。
- 浏览器和不同 JSON 库处理可能不一致。
- JSON `null` 能明确表达缺失值。

### Q8：为什么股票列表使用 LEFT JOIN？

- 主表股票必须全部显示。
- 收藏记录可能不存在。
- `LEFT JOIN` 可以在没有收藏时仍返回股票，并生成 `isFavorite=false`。

### Q9：为什么收藏表需要联合唯一索引？

- 同一用户不应重复收藏同一产品。
- 只在业务代码中先查再插会有并发竞争。
- 数据库唯一约束是最终一致性防线。

### Q10：当前登录系统最大的风险是什么？

- 明文密码数据库存储。
- 明文密码 localStorage 存储。
- 无服务端登录态。
- 接口通过可伪造 userId 识别用户。
- 用户数据可能越权。

### Q11：JWT 中应该存什么？

未来实现时可回答：

- 用户唯一 ID。
- 必要的角色或权限摘要。
- 签发时间和过期时间。
- Token ID（如果需要撤销和审计）。
- 不存密码、完整用户资料或敏感金融数据。

注意：这是未来设计知识，不是当前已实现能力。

### Q12：行情为什么适合缓存？

- 外部调用慢且不稳定。
- 同一代码和时间范围可能被重复查询。
- 历史 K 线变化频率低。
- 可以降低上游限流风险。

未来需要继续回答：缓存 Key、TTL、空值缓存、主动刷新和数据过期策略。当前尚未实现。

### Q13：为什么现在不拆成多个 Java 微服务？

- 当前业务规模小。
- 模块化单体更容易保证事务和开发效率。
- 微服务会引入服务发现、链路追踪、部署和分布式事务成本。
- Python 行情服务单独存在是因为语言生态边界，而不是为了堆微服务概念。

### Q14：Agent 为什么不应该直接访问数据库？

- 难以统一鉴权和字段权限。
- LLM 参数可能不可信。
- 写操作风险高。
- 应通过经过校验和审计的业务 Tool 调用 Service。
- Tool 输出应结构化、可追踪、可测试。

### Q15：MCP 和普通 REST API 有什么区别？

未来设计回答：

- REST API 面向普通程序客户端。
- MCP 为模型/Agent 提供标准化 Tool、Resource 和 Prompt 能力发现与调用。
- MCP Server 仍应调用 Spring Boot 受控 API，不应绕过业务规则直连数据库。
- MCP 不是替代全部 REST API 的理由。

---

## 13. 深入学习路线

采用“你实现、AI 提示和 Review”的方式，不再让 AI 直接完成核心代码。

### 阶段 1：Spring Boot 调用 Flask

目标调用链：

```text
Vue → Spring Boot → Flask → AkShare
```

你应当亲自实现：

1. `MarketServiceProperties`
2. `MarketDataClient`
3. Flask 响应 DTO
4. Java 行情 Controller
5. 连接超时和读取超时
6. 上游 400/502 映射
7. 单元测试

完成标准：

- Java 配置中没有硬编码 Flask 地址。
- Vue 不再请求 5000 端口。
- Flask 失败时 Java 返回明确错误。
- 能解释 `RestClient`、`WebClient` 和 `ProcessBuilder` 的取舍。

### 阶段 2：认证与用户隔离

你应当亲自实现：

1. Spring Security。
2. BCrypt。
3. JWT Access Token。
4. 当前用户上下文。
5. 登录/注册 DTO。
6. 不返回密码字段。
7. 收藏接口移除前端 `userId`。
8. 越权测试。

完成标准：

- 数据库不再存明文密码。
- localStorage 不再存明文密码。
- 用户 A 不能读写用户 B 的收藏。

### 阶段 3：数据库迁移和工程化

1. 使用 Flyway 建表。
2. 创建开发演示数据。
3. 数据库密码改为环境变量。
4. 清理无用依赖。
5. 统一 MyBatis 技术选择。
6. 添加 Java 集成测试。
7. 添加统一 README。

### 阶段 4：收支账单

只借鉴业务需求，不复制同学代码。

建议实现：

- 收入/支出流水。
- 账单分类。
- 月度收支汇总。
- 分类占比。
- 用户数据隔离。

暂不实现：

- 独立备忘录。
- 复杂管理员后台。
- 为了功能数量而增加的 CRUD。

### 阶段 5：投资组合

建议核心模型：

```text
portfolio
trade_record
position
asset_snapshot（后期）
```

必须学习：

- BigDecimal 精度。
- 买入、卖出与平均成本。
- 事务。
- 幂等。
- 并发更新。
- 当前市值和浮动盈亏。

### 阶段 6：风险测评

建议模型：

```text
risk_question
risk_option
risk_assessment
risk_answer
```

需要实现问卷、选项分数、总分规则、风险等级和产品适配提示。只有 `riskLevel` 字段不能称为风险测评。

### 阶段 7：Agent

先实现单 Agent + Tool Calling，不急于多 Agent。

第一组只读 Tools：

```text
query_transactions
summarize_monthly_spending
query_market_data
analyze_portfolio
```

要求：

- Tool 参数使用 Schema 校验。
- Tool 从认证上下文获得用户身份。
- LLM 不直接生成数据库 SQL。
- Tool 调用有日志和 request ID。
- 回答中的金额来自 Tool 结果，而非模型猜测。
- 对行情和投资内容增加非投资建议提示。

### 阶段 8：MCP

在 Agent Tools 稳定后，再把安全、只读能力暴露为 MCP：

```text
finance.get_monthly_summary
finance.get_portfolio
finance.get_financial_goals
market.get_stock_kline
market.get_fund_nav
```

第一版不开放买入、删除账单等敏感写操作。

---

## 14. 推荐学习工作流

每个模块执行：

```text
需求澄清
  → 你画调用链
  → 你写失败测试
  → 你实现最小代码
  → AI Code Review
  → 你根据 Review 修改
  → 运行验证
  → Explain-back
```

### 14.1 提示等级

- Level 1：只提示方向。
- Level 2：指出类、接口或官方文档。
- Level 3：提供伪代码和方法签名。
- Level 4：提供局部代码。
- Level 5：多次尝试后才提供完整实现。

默认从 Level 1 开始。

### 14.2 每个模块必须能回答

1. 它解决什么问题？
2. 请求经过哪些类？
3. 为什么这样分层？
4. 正常输入和异常输入分别是什么？
5. 数据库如何保证约束？
6. 并发时可能出现什么问题？
7. 测试覆盖了什么，没有覆盖什么？
8. 更简单和更复杂的替代方案是什么？

---

## 15. 本地启动与验证

### 15.1 Python 行情服务

```powershell
cd E:\GithubRepo\Java\Finance\market-service
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe run.py
```

验证：

```text
http://127.0.0.1:5000/health
http://127.0.0.1:5000/api/kline?code=000001&start=20250801&end=20250815
http://127.0.0.1:5000/api/fundchart?code=110022&start=20250801&end=20250815
```

测试：

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

### 15.2 Spring Boot

前提：本机 MySQL 已创建 `finance` 数据库及相关表，并且配置正确。

```powershell
cd E:\GithubRepo\Java\Finance\backend
mvn spring-boot:run
```

默认端口：

```text
81
```

注意：当前仓库缺少可靠的数据库迁移脚本，因此仅有代码不能保证新电脑直接启动成功。

### 15.3 Vue

```powershell
cd E:\GithubRepo\Java\Finance\frontend
npm install
npm run serve
```

当前生产构建没有在本文档生成时重新验证，不能声称构建已通过。

---

## 16. 面试前自测清单

### 项目介绍

- [ ] 能在 1 分钟内说明项目解决的问题。
- [ ] 能明确区分当前能力和未来计划。
- [ ] 不把依赖列表当成使用经验。
- [ ] 能解释为什么项目当前还不是完整投资组合系统。

### Java

- [ ] 能从 Controller 讲到 Mapper XML。
- [ ] 能解释 DTO、VO 和 Entity 的区别。
- [ ] 能解释 `LEFT JOIN` 和 `INNER JOIN`。
- [ ] 能指出当前登录和收藏的越权风险。
- [ ] 能解释为什么要用 BCrypt 和 JWT。
- [ ] 能说明当前 MyBatis/MyBatis-Plus 混用问题。

### Python

- [ ] 能解释 Application Factory。
- [ ] 能解释 Blueprint。
- [ ] 能解释 Route、Service、Client 边界。
- [ ] 能解释为什么外部失败返回 502。
- [ ] 能解释空数据与异常的区别。
- [ ] 能解释 `NaN` 为什么转为 `null`。
- [ ] 能解释基金累计收益率为什么稀疏。

### 数据库

- [ ] 能画出用户、股票、基金和收藏表关系。
- [ ] 能解释联合唯一索引。
- [ ] 能解释为什么不能只用“先查再插”防重复。
- [ ] 能指出缺少迁移脚本的问题。

### 测试

- [ ] 能说明 Python 10 个测试覆盖了什么。
- [ ] 能说明为什么测试替换外部 AkShare Client。
- [ ] 能解释单元测试与真实联网冒烟测试的区别。
- [ ] 能承认 Java 和 Vue 测试当前不足。

### AI Agent 与 MCP

- [ ] 能明确说明当前尚未实现。
- [ ] 能解释 Agent Tool 为什么调用 Service 而不是直连数据库。
- [ ] 能解释 MCP 的适用场景。
- [ ] 能说明为什么第一版只开放只读工具。
- [ ] 能说明金融场景中的幻觉、越权和提示注入风险。

---

## 17. 下一项学习任务

下一项建议只做一个小闭环：

> Spring Boot 调用 Flask `/health`，并通过 Java 暴露统一的行情服务健康检查接口。

暂时不要同时修改 K 线、基金、JWT、账单和 Agent。

验收要求：

1. Flask 地址来自配置，不硬编码。
2. Controller 不直接创建 HTTP Client。
3. Java DTO 能正确接收 Flask JSON。
4. Flask 不可连接时，Java 返回明确的上游错误。
5. 有自动化测试。
6. 由项目作者本人完成主要实现并进行 Explain-back。

完成这个小闭环后，再迁移 K 线和基金接口，让 Vue 只访问 Spring Boot。

---

## 18. 文档维护规则

每完成一个功能，都要同步更新：

1. “当前已实现”列表。
2. 架构图。
3. 接口表。
4. 测试状态。
5. 已知问题。
6. 简历描述。
7. 面试问题。

只有同时满足下面条件，才能把“未来计划”改成“已实现”：

- 代码存在。
- 测试或运行证据存在。
- 能独立解释设计和局限。
- 新电脑可以根据文档复现。

