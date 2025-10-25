<div align="center">
 <span>
 <img width="150" height="200" alt="Devr AI Logo" src="https://github.com/user-attachments/assets/ee93719e-0a40-488a-a18d-5394fd3ab8e3" />
 </span>

# 🤖 Devr.AI - AI-Powered Developer Relations Assistant
  
[![License:MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![GitHub Org's stars](https://img.shields.io/github/stars/AOSSIE-Org/Devr.AI?style=social)
[![Discord](https://img.shields.io/discord/1022871757289422898?color=7289da&logo=discord&logoColor=white)](https://discord.gg/BjaG8DJx2G)

</div>

Devr.AI is revolutionizing open-source community management with advanced AI-powered Developer Relations assistance. Built on cutting-edge LangGraph agent architecture, Devr.AI seamlessly integrates with Discord and GitHub to provide intelligent community support, streamline contributor onboarding, and deliver real-time project updates. By leveraging Large Language Models and workflow automation, Devr.AI reduces maintainer workload while enhancing contributor experience and project visibility.

### For in-depth documentation and internal workflow please refer [Notion](https://www.notion.so/Devr-AI-Design-and-Workflow-documenting-200881d7bed680bca517e9e53e1f7c3b)

## 🚀 Features

### 🧠 LangGraph Agent-Based Intelligence
- **ReAct Reasoning Pattern** - Think → Act → Observe workflow for intelligent decision making
- **Conversational Memory** - Persistent context across Discord sessions with automatic summarization
- **Multi-Tool Orchestration** - Dynamic tool selection including web search, FAQ, and GitHub operations
- **Self-Correcting Capabilities** - Iterative problem-solving with intelligent context awareness

### 💬 Discord Community Integration
- **Intelligent Message Processing** - Real-time classification and context-aware responses
- **GitHub Account Verification** - OAuth-based account linking for enhanced personalization
- **Command Interface** - Comprehensive bot commands for verification and management
- **Thread Management** - Organized conversation flows with persistent memory

### 🔗 GitHub Integration
- **OAuth Authentication** - Secure GitHub account linking and verification
- **User Profiling** - Automatic repository and contribution analysis
- **Repository Operations** - Read access and basic GitHub toolkit functionality
- **Cross-Platform Identity** - Unified profiles across Discord and GitHub

### 🏗️ Advanced Architecture
- **Asynchronous Processing** - RabbitMQ message queue with priority-based processing
- **Multi-Database System** - Supabase (PostgreSQL) + Weaviate (Vector DB) integration
- **Real-Time AI Responses** - Google Gemini LLM with Tavily web search capabilities
- **Agent Coordination** - LangGraph state management with persistent checkpointing

## 💻 Technologies Used

### Backend Services
- **LangGraph** - Multi-agent orchestration and workflow management
- **FastAPI** - High-performance async web framework
- **RabbitMQ** - Message queuing and asynchronous processing
- **Google Gemini** - Advanced LLM for reasoning and response generation

### AI & LLM Services
- **Gemini 2.5 Flash** - Primary reasoning and conversation model
- **Tavily Search API** - Real-time web information retrieval
- **Text Embeddings** - Semantic search and knowledge retrieval
- **ReAct Pattern** - Reasoning and Acting workflow implementation

### Data Storage
- **Supabase** - PostgreSQL database with authentication
- **Weaviate** - Vector database for semantic search
- **Agent Memory** - Persistent conversation context and state management

### Platform Integrations
- **Discord.py (py-cord)** - Modern Discord bot framework
- **PyGithub** - GitHub API integration and repository access
- **OAuth Integration** - Secure account linking and verification

### Frontend Dashboard
- **React + Vite** - Modern web interface with TypeScript
- **Tailwind CSS** - Responsive design system
- **Framer Motion** - Interactive UI animations

## 🔗 Repository Links

1. [Devr.AI Main Repository](https://github.com/AOSSIE-Org/Devr.AI)
2. [Devr.AI Frontend](https://github.com/AOSSIE-Org/Devr.AI/tree/main/frontend)
3. [Devr.AI Backend](https://github.com/AOSSIE-Org/Devr.AI/tree/main/backend)

## 🍀 Getting Started

Devr.AI utilizes a complex multi-service architecture with AI agents, message queues, and multiple databases. Setting up can be challenging, but we've streamlined the process.

**Quick Start:**
1. Clone the repository
2. Follow our comprehensive [Installation Guide](./docs/INSTALL_GUIDE.md)
3. Configure your environment variables (Discord bot, GitHub OAuth, API keys)
4. Set up Weaviate and Supabase databases
5. Run the development environment

For detailed setup instructions, troubleshooting, and deployment guides, please refer to our [Installation Guide](./docs/INSTALL_GUIDE.md).

## 🎯 Bot Commands

- `!verify_github` - Link your GitHub account for enhanced personalization
- `!verification_status` - Check your GitHub account linking status
- `!reset` - Clear conversation memory and start fresh
- `!help_devrel` - Display available commands and bot capabilities

<!-- TODO -->
<!-- ## 🎬 Feature Showcase

<div align="center">
<img width="1024" height="500" alt="Devr.AI_Feature_Graphic" src="[TO BE FILLED - FEATURE GRAPHIC]" />
</div>

## 📱 Screenshots

<div align="center">
 
| Discord Integration                                                                                                      | GitHub Verification                                                                                                     | Agent Dashboard                                                                                                         |
| :----------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------- |
| <img src="[TO BE FILLED - DISCORD SCREENSHOT]" width="260" height="auto" />                                            | <img src="[TO BE FILLED - GITHUB SCREENSHOT]" width="250" height="auto" />                                            | <img src="[TO BE FILLED - DASHBOARD SCREENSHOT]" width="250" height="auto" />                                         |

| Agent Workflow                                                                                                          | Memory Management                                                                                                       | Real-time Responses                                                                                                    |
| :---------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------- |
| <img src="[TO BE FILLED - WORKFLOW SCREENSHOT]" width="250" height="auto" />                                           | <img src="[TO BE FILLED - MEMORY SCREENSHOT]" width="250" height="auto" />                                            | <img src="[TO BE FILLED - RESPONSE SCREENSHOT]" width="250" height="auto"/>                                           |

</div> -->

## 🙌 Contributing

⭐ Don't forget to star this repository if you find it useful! ⭐

Thank you for considering contributing to Devr.AI! Contributions are highly appreciated and welcomed. To ensure a smooth collaboration, please refer to our [Contribution Guidelines](./CONTRIBUTING.md).

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Follow our coding standards and testing guidelines
4. Submit a pull request with detailed description

We appreciate your contributions and look forward to working with you to make developer relations more intelligent and efficient!

## ✨ Maintainers

- [Chandan S Gowda](https://github.com/chandansgowda)
- [Kartik Bhatt](https://github.com/smokeyScraper)

## 📬 Communication Channels

If you have questions, need clarifications, or want to discuss ideas, reach out through:

- [Discord Server](https://discord.gg/BjaG8DJx2G)
- [GitHub Discussions](https://github.com/AOSSIE-Org/Devr.AI/discussions/135)
- [Email](mailto:aossie.oss@gmail.com)

## 🎯 License

Distributed under the [MIT License](https://opensource.org/licenses/MIT). See [LICENSE](./LICENSE) for more information.

## 💪 Thanks To All Contributors

Thanks a lot for spending your time helping Devr.AI grow. Keep rocking 🥂

<a href="https://github.com/AOSSIE-Org/Devr.AI/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=AOSSIE-Org/Devr.AI" alt="Contributors"/>
</a>

---

<div align="center">
Built with ❤️ for the open-source developer community
</div>
