# System Architecture

## High-Level Architecture Diagram

```mermaid
graph TB
    subgraph "External APIs"
        RCA[REST Countries API]
        FA[Frankfurter API]
    end
    
    subgraph "Docker Compose Stack"
        subgraph "Application Layer"
            APP[FastAPI App<br/>:8000]
            API[API Routes<br/>Countries/Currencies/Health]
        end
        
        subgraph "Data Processing"
            AF_WS[Airflow Webserver<br/>:8080]
            AF_SCH[Airflow Scheduler]
            DAG1[Countries DAG]
            DAG2[Currencies DAG]
            DAG3[Combined DAG]
        end
        
        subgraph "Data Layer"
            PG[(PostgreSQL<br/>:5432<br/>countries_db)]
            PG_AF[(PostgreSQL<br/>:5433<br/>airflow_db)]
        end
        
        subgraph "Monitoring Stack"
            PROM[Prometheus<br/>:9090]
            GRAF[Grafana<br/>:3000]
        end
        
        subgraph "Processing Components"
            PROC1[Countries Processor]
            PROC2[Currency Processor]
            REPO[Database Repositories]
        end
    end
    
    subgraph "External Access"
        USER[Users/Developers]
        MON[Monitoring Users]
    end
    
    %% Data Flow
    RCA --> PROC1
    FA --> PROC2
    PROC1 --> REPO
    PROC2 --> REPO
    REPO --> PG
    
    %% API Flow
    USER --> APP
    APP --> API
    API --> REPO
    REPO --> PG
    
    %% Airflow Flow
    AF_SCH --> DAG1
    AF_SCH --> DAG2
    AF_SCH --> DAG3
    DAG1 --> PROC1
    DAG2 --> PROC2
    DAG3 --> PROC1
    DAG3 --> PROC2
    AF_WS --> AF_SCH
    AF_SCH --> PG_AF
    
    %% Monitoring Flow
    APP --> PROM
    PROM --> GRAF
    MON --> GRAF
    MON --> AF_WS
    
    %% Styling
    classDef api fill:#e1f5fe
    classDef database fill:#f3e5f5
    classDef monitoring fill:#e8f5e8
    classDef processing fill:#fff3e0
    classDef external fill:#fce4ec
    
    class RCA,FA external
    class PG,PG_AF database
    class PROM,GRAF monitoring
    class PROC1,PROC2,REPO,DAG1,DAG2,DAG3 processing
    class APP,API,AF_WS,AF_SCH api
```

## Detailed Component Architecture

```mermaid
graph LR
    subgraph "FastAPI Application"
        subgraph "API Layer"
            R1[Countries Routes]
            R2[Currency Routes]
            R3[Health Routes]
        end
        
        subgraph "Business Logic"
            M1[Monitoring Middleware]
            M2[Prometheus Metrics]
            M3[Request Tracking]
        end
        
        subgraph "Data Models"
            DM1[Country Model]
            DM2[Currency Model]
            DM3[API Response Models]
        end
    end
    
    subgraph "Data Processing Layer"
        subgraph "Processors"
            P1[Countries Processor]
            P2[Currency Processor]
            P3[Base Processor]
        end
        
        subgraph "API Clients"
            AC1[Countries API Client]
            AC2[Currency API Client]
            AC3[Base API Client]
        end
    end
    
    subgraph "Data Access Layer"
        subgraph "Repositories"
            REPO1[Country Repository]
            REPO2[Currency Repository]
        end
        
        subgraph "Database"
            DB[(PostgreSQL)]
            CONN[Connection Pool]
        end
    end
    
    subgraph "Infrastructure"
        subgraph "Orchestration"
            DC[Docker Compose]
            D1[App Container]
            D2[PostgreSQL Container]
            D3[Airflow Container]
            D4[Prometheus Container]
            D5[Grafana Container]
        end
        
        subgraph "Monitoring"
            METRICS[Prometheus Metrics]
            DASH[Grafana Dashboard]
            LOGS[Application Logs]
        end
    end
    
    %% Connections
    R1 --> P1
    R2 --> P2
    P1 --> AC1
    P2 --> AC2
    AC1 --> REPO1
    AC2 --> REPO2
    REPO1 --> CONN
    REPO2 --> CONN
    CONN --> DB
    
    M1 --> M2
    M2 --> METRICS
    METRICS --> DASH
    
    DC --> D1
    DC --> D2
    DC --> D3
    DC --> D4
    DC --> D5
```

## Data Flow Architecture

```mermaid
sequenceDiagram
    participant U as User
    participant API as FastAPI
    participant PROC as Processor
    participant EXT as External API
    participant DB as PostgreSQL
    participant PROM as Prometheus
    participant GRAF as Grafana
    
    Note over U,GRAF: Data Processing Flow
    
    U->>API: POST /countries/process
    API->>PROC: Start Countries Processing
    PROC->>EXT: Fetch Countries Data
    EXT-->>PROC: Countries JSON
    PROC->>DB: Save Countries
    DB-->>PROC: Success
    PROC-->>API: Processing Complete
    API->>PROM: Update Metrics
    API-->>U: Success Response
    
    Note over U,GRAF: API Request Flow
    
    U->>API: GET /countries/
    API->>PROM: Track Request
    API->>DB: Query Countries
    DB-->>API: Countries Data
    API-->>U: JSON Response
    
    Note over U,GRAF: Monitoring Flow
    
    PROM->>API: Scrape Metrics
    API-->>PROM: Metrics Data
    GRAF->>PROM: Query Metrics
    PROM-->>GRAF: Metrics Data
    U->>GRAF: View Dashboard
    GRAF-->>U: Monitoring Dashboard
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "Host Machine"
        subgraph "Docker Network"
            subgraph "Application Services"
                APP[FastAPI App<br/>Port: 8000]
                AF_WS[Airflow Webserver<br/>Port: 8080]
                AF_SCH[Airflow Scheduler]
            end
            
            subgraph "Data Services"
                PG[(PostgreSQL<br/>Port: 5432)]
                PG_AF[(Airflow DB<br/>Port: 5433)]
            end
            
            subgraph "Monitoring Services"
                PROM[Prometheus<br/>Port: 9090]
                GRAF[Grafana<br/>Port: 3000]
            end
        end
        
        subgraph "External Access"
            EXT1[API Clients]
            EXT2[Monitoring Users]
            EXT3[Airflow Users]
        end
        
        subgraph "External APIs"
            RCA[REST Countries API]
            FA[Frankfurter API]
        end
    end
    
    %% External connections
    EXT1 --> APP
    EXT2 --> GRAF
    EXT3 --> AF_WS
    
    %% Internal connections
    APP --> PG
    AF_WS --> PG_AF
    AF_SCH --> PG_AF
    APP --> PROM
    PROM --> GRAF
    
    %% External API connections
    APP --> RCA
    APP --> FA
    
    %% Styling
    classDef app fill:#e3f2fd
    classDef data fill:#f3e5f5
    classDef monitor fill:#e8f5e8
    classDef external fill:#fff3e0
    
    class APP,AF_WS,AF_SCH app
    class PG,PG_AF data
    class PROM,GRAF monitor
    class EXT1,EXT2,EXT3,RCA,FA external
```

## Technology Stack Architecture

```mermaid
graph LR
    subgraph "Frontend Layer"
        SWAGGER[Swagger UI]
        REDOC[ReDoc]
        GRAFANA[Grafana Dashboard]
        AIRFLOW[Airflow UI]
    end
    
    subgraph "API Layer"
        FASTAPI[FastAPI]
        PYDANTIC[Pydantic Models]
        MIDDLEWARE[Monitoring Middleware]
    end
    
    subgraph "Business Logic"
        PROCESSORS[Data Processors]
        REPOSITORIES[Data Repositories]
        VALIDATORS[Input Validators]
    end
    
    subgraph "Data Layer"
        POSTGRES[PostgreSQL]
        CONNECTION_POOL[Connection Pool]
        MIGRATIONS[Schema Migrations]
    end
    
    subgraph "Infrastructure"
        DOCKER[Docker]
        COMPOSE[Docker Compose]
        NETWORK[Docker Network]
    end
    
    subgraph "Monitoring"
        PROMETHEUS[Prometheus]
        GRAFANA_MON[Grafana]
        METRICS[Custom Metrics]
        LOGS[Structured Logging]
    end
    
    subgraph "Orchestration"
        AIRFLOW_ENGINE[Airflow Engine]
        DAGS[Workflow DAGs]
        SCHEDULER[Task Scheduler]
    end
    
    %% Connections
    SWAGGER --> FASTAPI
    REDOC --> FASTAPI
    FASTAPI --> PYDANTIC
    FASTAPI --> MIDDLEWARE
    MIDDLEWARE --> METRICS
    PROCESSORS --> REPOSITORIES
    REPOSITORIES --> CONNECTION_POOL
    CONNECTION_POOL --> POSTGRES
    DOCKER --> COMPOSE
    COMPOSE --> NETWORK
    PROMETHEUS --> GRAFANA_MON
    AIRFLOW_ENGINE --> DAGS
    DAGS --> SCHEDULER
```

This architecture documentation provides multiple views of your system:

1. **High-Level Architecture**: Shows the overall system components and their relationships
2. **Detailed Component Architecture**: Breaks down the internal structure of each component
3. **Data Flow Architecture**: Illustrates how data moves through the system
4. **Deployment Architecture**: Shows the physical deployment and network topology
5. **Technology Stack Architecture**: Maps the technology choices to architectural layers

You can:
1. **Copy any of these Mermaid diagrams** into GitHub (they render automatically)
2. **Use online Mermaid editors** to export as PNG/SVG
3. **Use the Mermaid CLI** to generate images locally
4. **Include them in your README.md** for better documentation

The diagrams showcase your production-grade architecture with proper separation of concerns, monitoring, and scalability considerations!
