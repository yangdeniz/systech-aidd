# Visual System Overview: HomeGuru в диаграммах

Комплексная визуализация архитектуры HomeGuru с разных точек зрения.

---

## 1. System Context Diagram

Система в окружении - взаимодействие с внешним миром.

```mermaid
graph TB
    User[👤 User<br/>Telegram Client]
    Bot[🏠 HomeGuru Bot<br/>Telegram Bot Application]
    TG[Telegram Bot API<br/>Telegram Servers]
    OR[OpenRouter API<br/>LLM Gateway]
    LLM1[Google Gemini<br/>Multimodal LLM]
    LLM2[Anthropic Claude<br/>Alternative LLM]
    Whisper[Faster-Whisper<br/>Local Model]
    
    User -->|текст/фото/аудио| TG
    TG -->|webhook/polling| Bot
    Bot -->|API requests| TG
    TG -->|ответы| User
    
    Bot -->|chat requests| OR
    OR -->|routing| LLM1
    OR -->|routing| LLM2
    OR -->|responses| Bot
    
    Bot -->|audio bytes| Whisper
    Whisper -->|transcribed text| Bot
    
    style User fill:#e1f5ff,stroke:#01579b,stroke-width:3px,color:#000
    style Bot fill:#fff3e0,stroke:#e65100,stroke-width:4px,color:#000
    style TG fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px,color:#000
    style OR fill:#f3e5f5,stroke:#4a148c,stroke-width:2px,color:#000
    style LLM1 fill:#fce4ec,stroke:#880e4f,stroke-width:2px,color:#000
    style LLM2 fill:#fce4ec,stroke:#880e4f,stroke-width:2px,color:#000
    style Whisper fill:#fff9c4,stroke:#f57f17,stroke-width:2px,color:#000
```

**Внешние зависимости:**
- **Telegram Bot API** - polling для получения обновлений
- **OpenRouter** - прокси для мультимодальных LLM
- **Faster-Whisper** - локальная модель (без внешних API)

---

## 2. Component Structure

Внутренняя структура приложения - компоненты и их связи.

```mermaid
graph TB
    subgraph "🤖 Telegram Layer"
        Bot[TelegramBot<br/>aiogram]
    end
    
    subgraph "🎮 Handlers Layer"
        CMD[CommandHandler<br/>команды]
        MSG[MessageHandler<br/>бизнес-логика]
    end
    
    subgraph "🔧 Services Layer"
        MEDIA[MediaProcessor<br/>фото/аудио]
        DLG[DialogueManager<br/>история]
        LLM[LLMClient<br/>OpenRouter]
    end
    
    subgraph "📋 Protocol Layer"
        IP[MediaProvider]
        IS[DialogueStorage]
        IL[LLMProvider]
    end
    
    subgraph "⚙️ Configuration Layer"
        CFG[Config<br/>.env + prompt]
    end
    
    Bot --> CMD
    Bot --> MSG
    MSG --> MEDIA
    MSG --> DLG
    MSG --> LLM
    CMD --> DLG
    
    MEDIA -.implements.-> IP
    DLG -.implements.-> IS
    LLM -.implements.-> IL
    
    MSG -.depends on.-> IP
    MSG -.depends on.-> IS
    MSG -.depends on.-> IL
    CMD -.depends on.-> IS
    
    CFG --> Bot
    CFG --> LLM
    CFG --> DLG
    CFG --> MEDIA
    
    style Bot fill:#fff3e0,stroke:#e65100,stroke-width:3px,color:#000
    style CMD fill:#f3e5f5,stroke:#4a148c,stroke-width:2px,color:#000
    style MSG fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px,color:#000
    style MEDIA fill:#fff9c4,stroke:#f57f17,stroke-width:2px,color:#000
    style DLG fill:#e0f2f1,stroke:#004d40,stroke-width:2px,color:#000
    style LLM fill:#fce4ec,stroke:#880e4f,stroke-width:2px,color:#000
    style IP fill:#e3f2fd,stroke:#0d47a1,stroke-width:2px,color:#000
    style IS fill:#e3f2fd,stroke:#0d47a1,stroke-width:2px,color:#000
    style IL fill:#e3f2fd,stroke:#0d47a1,stroke-width:2px,color:#000
    style CFG fill:#ffebee,stroke:#b71c1c,stroke-width:2px,color:#000
```

**Слои:**
- **Telegram Layer** - инфраструктура aiogram
- **Handlers Layer** - обработчики команд и сообщений
- **Services Layer** - бизнес-логика
- **Protocol Layer** - абстракции (SOLID DIP)
- **Configuration Layer** - настройки

---

## 3. Class Diagram

Основные классы и их отношения.

```mermaid
classDiagram
    class TelegramBot {
        +Dispatcher dp
        +MessageHandler message_handler
        +CommandHandler command_handler
        +start() void
        +handle_message(Message) void
        +handle_photo(Message) void
        +handle_voice(Message) void
        +cmd_start(Message) void
        +cmd_role(Message) void
        +cmd_reset(Message) void
        +cmd_help(Message) void
    }
    
    class MessageHandler {
        -LLMProvider llm
        -DialogueStorage storage
        -MediaProvider media
        +handle_user_message(user_id, username, text) str
        +handle_photo_message(user_id, username, caption, photo) str
        +handle_voice_message(user_id, username, voice) str
    }
    
    class CommandHandler {
        -DialogueStorage storage
        +get_start_message() str
        +get_role_message() str
        +get_help_message() str
        +reset_dialogue(user_id) str
    }
    
    class DialogueManager {
        -dict~int, list~ dialogues
        -int max_history
        +add_message(user_id, role, content) void
        +get_history(user_id) list
        +clear_history(user_id) void
    }
    
    class LLMClient {
        -OpenAI client
        -str model
        -str system_prompt
        +get_response(messages) str
    }
    
    class MediaProcessor {
        -WhisperModel model
        -str device
        +download_photo(bot, photo) bytes
        +photo_to_base64(photo_bytes) str
        +download_audio(bot, voice) bytes
        +transcribe_audio(audio_bytes) str
    }
    
    class Config {
        +str telegram_token
        +str openrouter_api_key
        +str openrouter_model
        +str system_prompt
        +int max_history
        +str whisper_model
        +str whisper_device
    }
    
    class LLMProvider {
        <<Protocol>>
        +get_response(messages) str
    }
    
    class DialogueStorage {
        <<Protocol>>
        +add_message(user_id, role, content) void
        +get_history(user_id) list
        +clear_history(user_id) void
    }
    
    class MediaProvider {
        <<Protocol>>
        +download_photo(bot, photo) bytes
        +photo_to_base64(photo_bytes) str
        +download_audio(bot, voice) bytes
        +transcribe_audio(audio_bytes) str
    }
    
    TelegramBot --> MessageHandler
    TelegramBot --> CommandHandler
    MessageHandler --> LLMProvider
    MessageHandler --> DialogueStorage
    MessageHandler --> MediaProvider
    CommandHandler --> DialogueStorage
    LLMClient ..|> LLMProvider
    DialogueManager ..|> DialogueStorage
    MediaProcessor ..|> MediaProvider
    Config ..> TelegramBot
    Config ..> LLMClient
    Config ..> DialogueManager
    Config ..> MediaProcessor
```

**Отношения:**
- `-->` композиция/агрегация
- `..>` использование (dependency)
- `..|>` реализация Protocol

---

## 4. Data Flow Diagram - Текстовое сообщение

Поток данных при обработке текста.

```mermaid
flowchart TD
    Start([👤 User sends text])
    Receive[TelegramBot receives Message]
    Extract[Extract user_id, username, text]
    Handle[MessageHandler.handle_user_message]
    AddUser[DialogueStorage.add_message<br/>role: user]
    GetHist[DialogueStorage.get_history]
    PrepMsg[Prepare messages<br/>system + history]
    CallLLM[LLMProvider.get_response]
    API[OpenRouter API call]
    Response[LLM response text]
    AddAssist[DialogueStorage.add_message<br/>role: assistant]
    Send[TelegramBot sends response]
    End([👤 User receives answer])
    
    Start --> Receive
    Receive --> Extract
    Extract --> Handle
    Handle --> AddUser
    AddUser --> GetHist
    GetHist --> PrepMsg
    PrepMsg --> CallLLM
    CallLLM --> API
    API --> Response
    Response --> AddAssist
    AddAssist --> Send
    Send --> End
    
    style Start fill:#e1f5ff,stroke:#01579b,stroke-width:2px,color:#000
    style Receive fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
    style Extract fill:#fff9c4,stroke:#f57f17,stroke-width:2px,color:#000
    style Handle fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px,color:#000
    style AddUser fill:#e0f2f1,stroke:#004d40,stroke-width:2px,color:#000
    style GetHist fill:#e0f2f1,stroke:#004d40,stroke-width:2px,color:#000
    style PrepMsg fill:#f3e5f5,stroke:#4a148c,stroke-width:2px,color:#000
    style CallLLM fill:#fce4ec,stroke:#880e4f,stroke-width:2px,color:#000
    style API fill:#e3f2fd,stroke:#0d47a1,stroke-width:2px,color:#000
    style Response fill:#fce4ec,stroke:#880e4f,stroke-width:2px,color:#000
    style AddAssist fill:#e0f2f1,stroke:#004d40,stroke-width:2px,color:#000
    style Send fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
    style End fill:#e1f5ff,stroke:#01579b,stroke-width:2px,color:#000
```

---

## 5. Data Flow Diagram - Фотография

Поток данных при обработке изображения.

```mermaid
flowchart TD
    Start([👤 User sends photo])
    Receive[TelegramBot receives Message]
    Extract[Extract user_id, username,<br/>caption, photo]
    Handle[MessageHandler.handle_photo_message]
    Download[MediaProvider.download_photo]
    Convert[MediaProvider.photo_to_base64]
    Format[Format multimodal message<br/>text + image_url]
    AddUser[DialogueStorage.add_message<br/>multimodal content]
    GetHist[DialogueStorage.get_history]
    PrepMsg[Prepare messages<br/>system + history + image]
    CallLLM[LLMProvider.get_response]
    VisionAPI[OpenRouter Vision API call]
    Response[LLM analyzes image<br/>+ returns text]
    AddAssist[DialogueStorage.add_message<br/>role: assistant]
    Send[TelegramBot sends response]
    End([👤 User receives analysis])
    
    Start --> Receive
    Receive --> Extract
    Extract --> Handle
    Handle --> Download
    Download --> Convert
    Convert --> Format
    Format --> AddUser
    AddUser --> GetHist
    GetHist --> PrepMsg
    PrepMsg --> CallLLM
    CallLLM --> VisionAPI
    VisionAPI --> Response
    Response --> AddAssist
    AddAssist --> Send
    Send --> End
    
    style Start fill:#e1f5ff,stroke:#01579b,stroke-width:2px,color:#000
    style Receive fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
    style Extract fill:#fff9c4,stroke:#f57f17,stroke-width:2px,color:#000
    style Handle fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px,color:#000
    style Download fill:#fff9c4,stroke:#f57f17,stroke-width:2px,color:#000
    style Convert fill:#fff9c4,stroke:#f57f17,stroke-width:2px,color:#000
    style Format fill:#f3e5f5,stroke:#4a148c,stroke-width:2px,color:#000
    style AddUser fill:#e0f2f1,stroke:#004d40,stroke-width:2px,color:#000
    style GetHist fill:#e0f2f1,stroke:#004d40,stroke-width:2px,color:#000
    style PrepMsg fill:#f3e5f5,stroke:#4a148c,stroke-width:2px,color:#000
    style CallLLM fill:#fce4ec,stroke:#880e4f,stroke-width:2px,color:#000
    style VisionAPI fill:#e3f2fd,stroke:#0d47a1,stroke-width:2px,color:#000
    style Response fill:#fce4ec,stroke:#880e4f,stroke-width:2px,color:#000
    style AddAssist fill:#e0f2f1,stroke:#004d40,stroke-width:2px,color:#000
    style Send fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
    style End fill:#e1f5ff,stroke:#01579b,stroke-width:2px,color:#000
```

---

## 6. Data Flow Diagram - Голосовое сообщение

Поток данных при обработке аудио.

```mermaid
flowchart TD
    Start([👤 User sends voice])
    Receive[TelegramBot receives Message]
    Extract[Extract user_id, username, voice]
    Handle[MessageHandler.handle_voice_message]
    Download[MediaProvider.download_audio]
    Transcribe[MediaProvider.transcribe_audio<br/>Faster-Whisper]
    LocalModel[Local Whisper Model<br/>base, CPU]
    TextResult[Transcribed text]
    Continue[Continue as text message]
    AddUser[DialogueStorage.add_message<br/>role: user, text]
    GetHist[DialogueStorage.get_history]
    CallLLM[LLMProvider.get_response]
    Response[LLM response text]
    AddAssist[DialogueStorage.add_message<br/>role: assistant]
    Send[TelegramBot sends response]
    End([👤 User receives answer])
    
    Start --> Receive
    Receive --> Extract
    Extract --> Handle
    Handle --> Download
    Download --> Transcribe
    Transcribe --> LocalModel
    LocalModel --> TextResult
    TextResult --> Continue
    Continue --> AddUser
    AddUser --> GetHist
    GetHist --> CallLLM
    CallLLM --> Response
    Response --> AddAssist
    AddAssist --> Send
    Send --> End
    
    style Start fill:#e1f5ff,stroke:#01579b,stroke-width:2px,color:#000
    style Receive fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
    style Extract fill:#fff9c4,stroke:#f57f17,stroke-width:2px,color:#000
    style Handle fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px,color:#000
    style Download fill:#fff9c4,stroke:#f57f17,stroke-width:2px,color:#000
    style Transcribe fill:#fff9c4,stroke:#f57f17,stroke-width:2px,color:#000
    style LocalModel fill:#fffde7,stroke:#f57f17,stroke-width:3px,color:#000
    style TextResult fill:#fff9c4,stroke:#f57f17,stroke-width:2px,color:#000
    style Continue fill:#f3e5f5,stroke:#4a148c,stroke-width:2px,color:#000
    style AddUser fill:#e0f2f1,stroke:#004d40,stroke-width:2px,color:#000
    style GetHist fill:#e0f2f1,stroke:#004d40,stroke-width:2px,color:#000
    style CallLLM fill:#fce4ec,stroke:#880e4f,stroke-width:2px,color:#000
    style Response fill:#fce4ec,stroke:#880e4f,stroke-width:2px,color:#000
    style AddAssist fill:#e0f2f1,stroke:#004d40,stroke-width:2px,color:#000
    style Send fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
    style End fill:#e1f5ff,stroke:#01579b,stroke-width:2px,color:#000
```

---

## 7. State Machine - Lifecycle диалога

Жизненный цикл диалога пользователя.

```mermaid
stateDiagram-v2
    [*] --> New: User sends /start
    New --> Active: First message
    Active --> Active: User sends message
    Active --> Active: Bot responds
    Active --> Active: Photo/Voice processed
    Active --> HistoryLimit: History exceeds MAX_HISTORY
    HistoryLimit --> Active: Old messages trimmed
    Active --> Cleared: User sends /reset
    Cleared --> Active: New message
    Active --> [*]: Bot restart (in-memory loss)
    
    note right of New
        Empty history
        No messages
    end note
    
    note right of Active
        Messages in history
        Context maintained
    end note
    
    note right of HistoryLimit
        FIFO cleanup
        Keep last N messages
    end note
    
    note right of Cleared
        History deleted
        Fresh start
    end note
```

**Состояния:**
- **New** - пользователь только начал (/start)
- **Active** - активный диалог с историей
- **HistoryLimit** - превышен лимит, очистка старых сообщений
- **Cleared** - пользователь сбросил историю (/reset)

---

## 8. Deployment Diagram

Развертывание компонентов в runtime.

```mermaid
graph TB
    subgraph "🖥 Local Machine / Server"
        subgraph "Python Process"
            Main[main.py<br/>Entry Point]
            Bot[TelegramBot<br/>aiogram]
            Handlers[Handlers Layer]
            Services[Services Layer]
        end
        
        subgraph "File System"
            Env[.env<br/>Configuration]
            Prompt[system_prompt.txt<br/>Role Definition]
            Logs[bot.log<br/>Application Logs]
            Model[Whisper Model<br/>~140MB base]
        end
        
        subgraph "Memory"
            Dialogues[dict<br/>user_id → messages<br/>In-Memory Storage]
        end
    end
    
    subgraph "☁️ External Services"
        TG[Telegram Servers<br/>Bot API]
        OR[OpenRouter<br/>LLM Gateway]
    end
    
    Main --> Env
    Main --> Prompt
    Main --> Bot
    Bot --> Handlers
    Handlers --> Services
    Services --> Dialogues
    Services --> Model
    Bot --> Logs
    
    Bot <-->|HTTPS Polling| TG
    Services <-->|HTTPS API| OR
    
    style Main fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
    style Bot fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
    style Handlers fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px,color:#000
    style Services fill:#e0f2f1,stroke:#004d40,stroke-width:2px,color:#000
    style Env fill:#ffebee,stroke:#b71c1c,stroke-width:2px,color:#000
    style Prompt fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px,color:#000
    style Logs fill:#fff9c4,stroke:#f57f17,stroke-width:2px,color:#000
    style Model fill:#fffde7,stroke:#f57f17,stroke-width:2px,color:#000
    style Dialogues fill:#fce4ec,stroke:#880e4f,stroke-width:2px,color:#000
    style TG fill:#e3f2fd,stroke:#0d47a1,stroke-width:2px,color:#000
    style OR fill:#f3e5f5,stroke:#4a148c,stroke-width:2px,color:#000
```

**Runtime компоненты:**
- **Python Process** - один процесс приложения
- **File System** - конфигурация и логи
- **Memory** - in-memory хранилище диалогов
- **External Services** - Telegram и OpenRouter

---

## 9. Module Dependencies

Зависимости между модулями (import graph).

```mermaid
graph TB
    main[main.py]
    bot[bot.py]
    msg[message_handler.py]
    cmd[command_handler.py]
    llm[llm_client.py]
    dlg[dialogue_manager.py]
    media[media_processor.py]
    cfg[config.py]
    iface[interfaces.py]
    
    main --> bot
    main --> msg
    main --> cmd
    main --> llm
    main --> dlg
    main --> media
    main --> cfg
    
    bot --> msg
    bot --> cmd
    
    msg --> iface
    cmd --> iface
    
    llm -.implements.-> iface
    dlg -.implements.-> iface
    media -.implements.-> iface
    
    style main fill:#fff3e0,stroke:#e65100,stroke-width:3px,color:#000
    style bot fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
    style msg fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px,color:#000
    style cmd fill:#f3e5f5,stroke:#4a148c,stroke-width:2px,color:#000
    style llm fill:#fce4ec,stroke:#880e4f,stroke-width:2px,color:#000
    style dlg fill:#e0f2f1,stroke:#004d40,stroke-width:2px,color:#000
    style media fill:#fff9c4,stroke:#f57f17,stroke-width:2px,color:#000
    style cfg fill:#ffebee,stroke:#b71c1c,stroke-width:2px,color:#000
    style iface fill:#e3f2fd,stroke:#0d47a1,stroke-width:3px,color:#000
```

**Направление зависимостей:**
- `main.py` - точка входа, зависит от всех
- `interfaces.py` - не зависит ни от кого (контракты)
- Сервисы реализуют Protocol из `interfaces.py`
- Handlers зависят от Protocol, не от реализаций

---

## 10. Protocol Contracts (SOLID DIP)

Dependency Inversion через Protocol.

```mermaid
graph TB
    subgraph "High Level"
        MSG[MessageHandler<br/>бизнес-логика]
        CMD[CommandHandler<br/>команды]
    end
    
    subgraph "Abstractions (Protocol)"
        LP[LLMProvider<br/>Protocol]
        DS[DialogueStorage<br/>Protocol]
        MP[MediaProvider<br/>Protocol]
    end
    
    subgraph "Low Level"
        LLM[LLMClient<br/>OpenRouter]
        DLG[DialogueManager<br/>In-Memory]
        MEDIA[MediaProcessor<br/>Whisper]
    end
    
    subgraph "Alternative Implementations"
        LLM2[AnthropicClient<br/>Direct API]
        DLG2[RedisDialogueManager<br/>Persistent]
        MEDIA2[CloudMediaProcessor<br/>Cloud STT]
    end
    
    MSG -.depends on.-> LP
    MSG -.depends on.-> DS
    MSG -.depends on.-> MP
    CMD -.depends on.-> DS
    
    LLM -.implements.-> LP
    DLG -.implements.-> DS
    MEDIA -.implements.-> MP
    
    LLM2 -.can implement.-> LP
    DLG2 -.can implement.-> DS
    MEDIA2 -.can implement.-> MP
    
    style MSG fill:#e8f5e9,stroke:#1b5e20,stroke-width:3px,color:#000
    style CMD fill:#f3e5f5,stroke:#4a148c,stroke-width:3px,color:#000
    style LP fill:#e3f2fd,stroke:#0d47a1,stroke-width:3px,color:#000
    style DS fill:#e3f2fd,stroke:#0d47a1,stroke-width:3px,color:#000
    style MP fill:#e3f2fd,stroke:#0d47a1,stroke-width:3px,color:#000
    style LLM fill:#fce4ec,stroke:#880e4f,stroke-width:2px,color:#000
    style DLG fill:#e0f2f1,stroke:#004d40,stroke-width:2px,color:#000
    style MEDIA fill:#fff9c4,stroke:#f57f17,stroke-width:2px,color:#000
    style LLM2 fill:#ffebee,stroke:#880e4f,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    style DLG2 fill:#ffebee,stroke:#004d40,stroke-width:2px,color:#000,stroke-dasharray: 5 5
    style MEDIA2 fill:#ffebee,stroke:#f57f17,stroke-width:2px,color:#000,stroke-dasharray: 5 5
```

**Преимущества DIP:**
- High-level modules зависят от абстракций
- Low-level реализации заменяемы
- Легко тестировать (моки Protocol)
- Легко расширять (новые реализации)

---

## 11. Data Structure - Message Format

Структура данных сообщений.

```mermaid
graph TB
    subgraph "Text Message"
        TM[Message Object]
        TM1[role: str]
        TM2[content: str]
        TM --> TM1
        TM --> TM2
    end
    
    subgraph "Multimodal Message (Photo)"
        MM[Message Object]
        MM1[role: str = 'user']
        MM2[content: list]
        MM21[TextPart]
        MM211[type: 'text']
        MM212[text: str]
        MM22[ImagePart]
        MM221[type: 'image_url']
        MM222[image_url]
        MM2221[url: str base64]
        
        MM --> MM1
        MM --> MM2
        MM2 --> MM21
        MM2 --> MM22
        MM21 --> MM211
        MM21 --> MM212
        MM22 --> MM221
        MM22 --> MM222
        MM222 --> MM2221
    end
    
    subgraph "History Structure"
        H[dialogues: dict]
        H1[user_id: int]
        H2[messages: list]
        H21[Message 1]
        H22[Message 2]
        H23[Message N]
        
        H --> H1
        H1 --> H2
        H2 --> H21
        H2 --> H22
        H2 --> H23
    end
    
    style TM fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px,color:#000
    style TM1 fill:#c8e6c9,stroke:#1b5e20,stroke-width:1px,color:#000
    style TM2 fill:#c8e6c9,stroke:#1b5e20,stroke-width:1px,color:#000
    style MM fill:#e3f2fd,stroke:#0d47a1,stroke-width:2px,color:#000
    style MM1 fill:#bbdefb,stroke:#0d47a1,stroke-width:1px,color:#000
    style MM2 fill:#bbdefb,stroke:#0d47a1,stroke-width:1px,color:#000
    style MM21 fill:#90caf9,stroke:#0d47a1,stroke-width:1px,color:#000
    style MM211 fill:#64b5f6,stroke:#0d47a1,stroke-width:1px,color:#000
    style MM212 fill:#64b5f6,stroke:#0d47a1,stroke-width:1px,color:#000
    style MM22 fill:#90caf9,stroke:#0d47a1,stroke-width:1px,color:#000
    style MM221 fill:#64b5f6,stroke:#0d47a1,stroke-width:1px,color:#000
    style MM222 fill:#64b5f6,stroke:#0d47a1,stroke-width:1px,color:#000
    style MM2221 fill:#42a5f5,stroke:#0d47a1,stroke-width:1px,color:#000
    style H fill:#fce4ec,stroke:#880e4f,stroke-width:2px,color:#000
    style H1 fill:#f8bbd0,stroke:#880e4f,stroke-width:1px,color:#000
    style H2 fill:#f8bbd0,stroke:#880e4f,stroke-width:1px,color:#000
    style H21 fill:#f48fb1,stroke:#880e4f,stroke-width:1px,color:#000
    style H22 fill:#f48fb1,stroke:#880e4f,stroke-width:1px,color:#000
    style H23 fill:#f48fb1,stroke:#880e4f,stroke-width:1px,color:#000
```

---

## 12. Testing Architecture

Структура тестирования.

```mermaid
graph TB
    subgraph "Tests Layer"
        TC[Test Cases<br/>66 tests, 98% coverage]
        CF[conftest.py<br/>Fixtures]
    end
    
    subgraph "Fixtures"
        F1[dialogue_manager]
        F2[mock_llm_client]
        F3[mock_message]
        F4[mock_media_provider]
    end
    
    subgraph "Test Files"
        T1[test_bot.py]
        T2[test_message_handler.py]
        T3[test_command_handler.py]
        T4[test_dialogue_manager.py]
        T5[test_llm_client.py]
        T6[test_media_processor.py]
        T7[test_config.py]
        T8[test_main.py]
    end
    
    subgraph "Source Code"
        S1[bot.py]
        S2[message_handler.py]
        S3[command_handler.py]
        S4[dialogue_manager.py]
        S5[llm_client.py]
        S6[media_processor.py]
        S7[config.py]
        S8[main.py]
    end
    
    CF --> F1
    CF --> F2
    CF --> F3
    CF --> F4
    
    T1 --> F1
    T1 --> F2
    T1 --> F3
    T2 --> F1
    T2 --> F2
    T2 --> F4
    T3 --> F1
    T4 --> F1
    
    T1 -.tests.-> S1
    T2 -.tests.-> S2
    T3 -.tests.-> S3
    T4 -.tests.-> S4
    T5 -.tests.-> S5
    T6 -.tests.-> S6
    T7 -.tests.-> S7
    T8 -.tests.-> S8
    
    style TC fill:#e8f5e9,stroke:#1b5e20,stroke-width:3px,color:#000
    style CF fill:#fff9c4,stroke:#f57f17,stroke-width:2px,color:#000
    style F1 fill:#fff9c4,stroke:#f57f17,stroke-width:1px,color:#000
    style F2 fill:#fff9c4,stroke:#f57f17,stroke-width:1px,color:#000
    style F3 fill:#fff9c4,stroke:#f57f17,stroke-width:1px,color:#000
    style F4 fill:#fff9c4,stroke:#f57f17,stroke-width:1px,color:#000
```

---

## 13. Error Handling Flow

Обработка ошибок в системе.

```mermaid
flowchart TD
    Start[User Action]
    Try{Try Block}
    Success[Process Successfully]
    Catch{Exception Type?}
    
    E1[Telegram API Error]
    E2[OpenRouter Error]
    E3[Whisper Error]
    E4[Config Error]
    E5[Unknown Error]
    
    L1[Log Error<br/>bot.log]
    L2[Log Error<br/>bot.log]
    L3[Log Error<br/>bot.log]
    L4[Log Error<br/>exit]
    L5[Log Error<br/>bot.log]
    
    R1[Retry or<br/>Inform User]
    R2[Send Error Message<br/>to User]
    R3[Skip Voice<br/>Inform User]
    R4[Bot Stops]
    R5[Generic Error<br/>Message to User]
    
    Start --> Try
    Try -->|No Error| Success
    Try -->|Error| Catch
    
    Catch -->|aiogram exception| E1
    Catch -->|API error| E2
    Catch -->|transcribe error| E3
    Catch -->|missing config| E4
    Catch -->|other| E5
    
    E1 --> L1 --> R1
    E2 --> L2 --> R2
    E3 --> L3 --> R3
    E4 --> L4 --> R4
    E5 --> L5 --> R5
    
    style Start fill:#e1f5ff,stroke:#01579b,stroke-width:2px,color:#000
    style Try fill:#fff9c4,stroke:#f57f17,stroke-width:2px,color:#000
    style Success fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px,color:#000
    style Catch fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
    style E1 fill:#ffebee,stroke:#b71c1c,stroke-width:2px,color:#000
    style E2 fill:#ffebee,stroke:#b71c1c,stroke-width:2px,color:#000
    style E3 fill:#ffebee,stroke:#b71c1c,stroke-width:2px,color:#000
    style E4 fill:#ffebee,stroke:#b71c1c,stroke-width:2px,color:#000
    style E5 fill:#ffebee,stroke:#b71c1c,stroke-width:2px,color:#000
    style L1 fill:#f3e5f5,stroke:#4a148c,stroke-width:2px,color:#000
    style L2 fill:#f3e5f5,stroke:#4a148c,stroke-width:2px,color:#000
    style L3 fill:#f3e5f5,stroke:#4a148c,stroke-width:2px,color:#000
    style L4 fill:#f3e5f5,stroke:#4a148c,stroke-width:2px,color:#000
    style L5 fill:#f3e5f5,stroke:#4a148c,stroke-width:2px,color:#000
```

---

## Резюме по диаграммам

### Создано 13 диаграмм:

1. **System Context** - внешнее окружение
2. **Component Structure** - внутренние компоненты и слои
3. **Class Diagram** - классы и их отношения
4. **Data Flow (Text)** - обработка текста
5. **Data Flow (Photo)** - обработка фотографий
6. **Data Flow (Voice)** - обработка аудио
7. **State Machine** - жизненный цикл диалога
8. **Deployment** - runtime развертывание
9. **Module Dependencies** - зависимости между модулями
10. **Protocol Contracts** - SOLID DIP визуализация
11. **Data Structure** - форматы данных
12. **Testing Architecture** - структура тестов
13. **Error Handling** - обработка ошибок

### Типы диаграмм:
- 📊 **Структурные** - компоненты, классы, модули
- 🔄 **Поведенческие** - потоки данных, state machine
- 🚀 **Развертывания** - deployment, dependencies
- 🧪 **Тестирование** - test architecture
- ⚠️ **Обработка ошибок** - error flow

### Цветовая схема:
- **Оранжевый** - Telegram инфраструктура
- **Зеленый** - бизнес-логика, обработчики
- **Голубой** - Protocol абстракции, внешние API
- **Фиолетовый** - команды, конфигурация
- **Розовый** - LLM, хранилище
- **Желтый** - медиа-обработка
- **Красный** - конфигурация, ошибки

---

## Дополнительные материалы

- **Architecture Overview:** [`03-architecture-overview.md`](03-architecture-overview.md)
- **Developer Quickstart:** [`02-developer-quickstart.md`](02-developer-quickstart.md)
- **Configuration Guide:** [`07-configuration.md`](07-configuration.md)
- **Техническое видение:** `../vision.md`
- **ADRs:** `../addrs/`

