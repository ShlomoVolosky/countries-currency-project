# POC System Architecture

## Simple POC Architecture Overview

```mermaid
graph TB
    subgraph "External APIs"
        RCA[REST Countries API<br/>restcountries.com]
        FA[Frankfurter API<br/>api.frankfurter.app]
    end
    
    subgraph "Python Application"
        subgraph "Core Components"
            P1[part1_countries.py<br/>Fetch Countries Data]
            P2[part2_currencies.py<br/>Get Exchange Rates]
            P3[part3_scheduler.py<br/>Automated Scheduler]
        end
        
        subgraph "Supporting Modules"
            CONFIG[config.py<br/>Configuration]
            DB[database.py<br/>Database Operations]
        end
    end
    
    subgraph "Data Storage"
        PG[(PostgreSQL<br/>countries_db)]
    end
    
    subgraph "Testing"
        TESTS[Test Suite<br/>pytest]
    end
    
    subgraph "User Interaction"
        USER[Developer/User]
    end
    
    %% Data Flow
    RCA --> P1
    FA --> P2
    P1 --> DB
    P2 --> DB
    DB --> PG
    P3 --> P1
    P3 --> P2
    
    %% User Flow
    USER --> P1
    USER --> P2
    USER --> P3
    
    %% Testing
    TESTS --> P1
    TESTS --> P2
    TESTS --> P3
    TESTS --> DB
    
    %% Configuration
    CONFIG --> P1
    CONFIG --> P2
    CONFIG --> P3
    CONFIG --> DB
    
    %% Styling
    classDef api fill:#e1f5fe
    classDef python fill:#fff3e0
    classDef database fill:#f3e5f5
    classDef testing fill:#e8f5e8
    classDef user fill:#fce4ec
    
    class RCA,FA api
    class P1,P2,P3,CONFIG,DB python
    class PG database
    class TESTS testing
    class USER user
```

## Detailed Component Architecture

```mermaid
graph LR
    subgraph "part1_countries.py"
        P1_FETCH[Fetch Countries<br/>from REST API]
        P1_PARSE[Parse JSON<br/>Response]
        P1_SAVE[Save to<br/>Database]
    end
    
    subgraph "part2_currencies.py"
        P2_GET[Get Currencies<br/>from Database]
        P2_FETCH[Fetch Exchange<br/>Rates from API]
        P2_SAVE[Save Rates<br/>to Database]
    end
    
    subgraph "part3_scheduler.py"
        P3_MENU[Interactive<br/>Menu]
        P3_SCHED[Schedule<br/>Updates]
        P3_RUN[Run Parts<br/>Automatically]
    end
    
    subgraph "database.py"
        DB_CONN[Database<br/>Connection]
        DB_QUERY[SQL<br/>Queries]
        DB_TRANS[Transaction<br/>Management]
    end
    
    subgraph "config.py"
        CFG_ENV[Environment<br/>Variables]
        CFG_DB[Database<br/>Config]
        CFG_API[API<br/>Config]
    end
    
    subgraph "PostgreSQL"
        TBL_COUNTRIES[countries<br/>table]
        TBL_RATES[currency_rates<br/>table]
    end
    
    %% Connections
    P1_FETCH --> P1_PARSE
    P1_PARSE --> P1_SAVE
    P1_SAVE --> DB_QUERY
    
    P2_GET --> DB_QUERY
    P2_FETCH --> P2_SAVE
    P2_SAVE --> DB_QUERY
    
    P3_MENU --> P3_SCHED
    P3_SCHED --> P3_RUN
    P3_RUN --> P1_FETCH
    P3_RUN --> P2_GET
    
    DB_QUERY --> DB_CONN
    DB_CONN --> TBL_COUNTRIES
    DB_CONN --> TBL_RATES
    
    CFG_ENV --> CFG_DB
    CFG_DB --> DB_CONN
    CFG_API --> P1_FETCH
    CFG_API --> P2_FETCH
```

## Data Flow Architecture

```mermaid
sequenceDiagram
    participant U as User
    participant P1 as part1_countries.py
    participant P2 as part2_currencies.py
    participant P3 as part3_scheduler.py
    participant DB as database.py
    participant PG as PostgreSQL
    participant RCA as REST Countries API
    participant FA as Frankfurter API
    
    Note over U,FA: Initial Data Loading Flow
    
    U->>P1: Run part1_countries.py
    P1->>RCA: GET /v3.1/all
    RCA-->>P1: Countries JSON
    P1->>DB: Save countries data
    DB->>PG: INSERT INTO countries
    PG-->>DB: Success
    DB-->>P1: Data saved
    P1-->>U: Countries loaded
    
    Note over U,FA: Currency Rates Flow
    
    U->>P2: Run part2_currencies.py
    P2->>DB: Get countries with currencies
    DB->>PG: SELECT currencies FROM countries
    PG-->>DB: Currency data
    DB-->>P2: Currency list
    P2->>FA: GET /latest?from=USD&to=ILS
    FA-->>P2: Exchange rates
    P2->>DB: Save exchange rates
    DB->>PG: INSERT INTO currency_rates
    PG-->>DB: Success
    DB-->>P2: Rates saved
    P2-->>U: Currency rates loaded
    
    Note over U,FA: Automated Scheduler Flow
    
    U->>P3: Run part3_scheduler.py
    P3-->>U: Show menu options
    U->>P3: Choose option
    P3->>P1: Execute countries update
    P1->>RCA: Fetch latest data
    RCA-->>P1: Updated countries
    P1->>DB: Update countries
    P3->>P2: Execute currency update
    P2->>FA: Fetch latest rates
    FA-->>P2: Updated rates
    P2->>DB: Update rates
    P3-->>U: Update complete
```

## Simple Deployment Architecture

```mermaid
graph TB
    subgraph "Development Machine"
        subgraph "Python Environment"
            VENV[Virtual Environment<br/>venv/]
            DEPS[Python Dependencies<br/>requirements.txt]
        end
        
        subgraph "Application Files"
            SRC[Source Code<br/>src/]
            TESTS[Test Files<br/>tests/]
            SQL[Database Schema<br/>sql/]
        end
        
        subgraph "Configuration"
            ENV[Environment File<br/>.env]
            CONFIG[Config Module<br/>config.py]
        end
    end
    
    subgraph "External Services"
        RCA[REST Countries API<br/>restcountries.com]
        FA[Frankfurter API<br/>api.frankfurter.app]
    end
    
    subgraph "Local Database"
        PG[(PostgreSQL<br/>localhost:5432)]
    end
    
    subgraph "User Interface"
        TERMINAL[Command Line<br/>Terminal]
        IDE[Code Editor<br/>IDE]
    end
    
    %% Connections
    TERMINAL --> SRC
    IDE --> SRC
    SRC --> VENV
    VENV --> DEPS
    SRC --> CONFIG
    CONFIG --> ENV
    SRC --> PG
    SRC --> RCA
    SRC --> FA
    TESTS --> SRC
    SQL --> PG
    
    %% Styling
    classDef python fill:#fff3e0
    classDef external fill:#e1f5fe
    classDef database fill:#f3e5f5
    classDef interface fill:#e8f5e8
    
    class VENV,DEPS,SRC,TESTS,CONFIG,ENV python
    class RCA,FA external
    class PG database
    class TERMINAL,IDE interface
```

## Technology Stack Architecture

```mermaid
graph TB
    subgraph "Application Layer"
        PYTHON[Python 3.x<br/>Core Language]
        REQUESTS[requests<br/>HTTP Client]
        PSYCOPG2[psycopg2<br/>PostgreSQL Driver]
    end
    
    subgraph "Data Layer"
        POSTGRES[PostgreSQL<br/>Database]
        SQL[SQL<br/>Query Language]
    end
    
    subgraph "External APIs"
        REST_API[REST Countries API<br/>Country Data]
        CURRENCY_API[Frankfurter API<br/>Exchange Rates]
    end
    
    subgraph "Development Tools"
        PYTEST[pytest<br/>Testing Framework]
        VENV[venv<br/>Virtual Environment]
        PIP[pip<br/>Package Manager]
    end
    
    subgraph "Configuration"
        ENV[Environment Variables<br/>.env file]
        CONFIG[Configuration Module<br/>config.py]
    end
    
    %% Connections
    PYTHON --> REQUESTS
    PYTHON --> PSYCOPG2
    REQUESTS --> REST_API
    REQUESTS --> CURRENCY_API
    PSYCOPG2 --> POSTGRES
    POSTGRES --> SQL
    PYTEST --> PYTHON
    VENV --> PYTHON
    PIP --> VENV
    ENV --> CONFIG
    CONFIG --> PYTHON
    
    %% Styling
    classDef app fill:#fff3e0
    classDef data fill:#f3e5f5
    classDef external fill:#e1f5fe
    classDef tools fill:#e8f5e8
    classDef config fill:#fce4ec
    
    class PYTHON,REQUESTS,PSYCOPG2 app
    class POSTGRES,SQL data
    class REST_API,CURRENCY_API external
    class PYTEST,VENV,PIP tools
    class ENV,CONFIG config
```

## Simple Process Flow

```mermaid
flowchart TD
    START([Start]) --> CHOICE{Choose Operation}
    
    CHOICE -->|Option 1| P1[Run part1_countries.py]
    CHOICE -->|Option 2| P2[Run part2_currencies.py]
    CHOICE -->|Option 3| P3[Run part3_scheduler.py]
    CHOICE -->|Option 4| TEST[Run Tests]
    
    P1 --> FETCH1[Fetch Countries from API]
    FETCH1 --> PARSE1[Parse JSON Response]
    PARSE1 --> SAVE1[Save to Database]
    SAVE1 --> SUCCESS1[Countries Loaded]
    
    P2 --> GET_CURR[Get Currencies from DB]
    GET_CURR --> FETCH2[Fetch Exchange Rates]
    FETCH2 --> PARSE2[Parse Rate Data]
    PARSE2 --> SAVE2[Save Rates to DB]
    SAVE2 --> SUCCESS2[Rates Loaded]
    
    P3 --> MENU[Show Menu Options]
    MENU --> SCHED_CHOICE{Choose Schedule}
    SCHED_CHOICE -->|Manual| MANUAL[Run Parts Manually]
    SCHED_CHOICE -->|Auto| AUTO[Schedule Automatic Updates]
    MANUAL --> P1
    AUTO --> SCHEDULER[Set up Scheduler]
    SCHEDULER --> WAIT[Wait for Schedule]
    WAIT --> P1
    
    TEST --> RUN_TESTS[Execute pytest]
    RUN_TESTS --> TEST_RESULTS[Show Results]
    
    SUCCESS1 --> END([End])
    SUCCESS2 --> END
    TEST_RESULTS --> END
    
    %% Styling
    classDef start fill:#e8f5e8
    classDef process fill:#fff3e0
    classDef decision fill:#e1f5fe
    classDef end fill:#fce4ec
    
    class START,END start
    class P1,P2,P3,TEST,FETCH1,PARSE1,SAVE1,GET_CURR,FETCH2,PARSE2,SAVE2,MENU,MANUAL,AUTO,SCHEDULER,WAIT,RUN_TESTS process
    class CHOICE,SCHED_CHOICE decision
    class SUCCESS1,SUCCESS2,TEST_RESULTS end
```

This architecture documentation represents the simple POC version with:

1. **Simple Component Architecture**: Basic Python scripts with clear separation of concerns
2. **Data Flow**: Straightforward data fetching and storage process
3. **Deployment**: Local development setup with minimal dependencies
4. **Technology Stack**: Simple, lightweight technology choices
5. **Process Flow**: Clear step-by-step execution flow

The POC version focuses on demonstrating core functionality with minimal complexity, making it easy to understand and extend.
