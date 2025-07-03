/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onMounted, useRef } from "@odoo/owl";
import { rpc } from "@web/core/network/rpc";

class AIAgentSystray extends Component {
    setup() {
        this.state = useState({
            messages: [],
            inputMessage: "",
            isOpen: false,
            isLoading: false,
        });
        this.chatContainerRef = useRef("chatContainer");
        onMounted(() => {
            this.state.messages.push({
                content: "Hello! How can I help you with Odoo today?",
                isUser: false
            });
        });
    }

    async sendMessage() {
        const messageText = this.state.inputMessage.trim();
        if (!messageText || this.state.isLoading) return;

        // Add user message to UI immediately
        this.state.messages.push({ content: messageText, isUser: true });
        this.state.inputMessage = "";
        this.state.isLoading = true;
        this.scrollToBottom();

        // Prepare the conversation history for the AI
        const conversationHistory = this.state.messages.slice(0, -1).map(msg => ({
            role: msg.isUser ? "user" : "assistant",
            content: msg.content
        }));

        try {
            // Use rpc to get the configuration from the Odoo backend.
            const config = await rpc("/ai_agent/get_config", {});
            if (!config || !config.ai_agent_url || !config.ai_agent_api_key) {
                throw new Error("AI Agent URL is not configured in Odoo's System Parameters.");
            }

            // Make the call to your Python AI service
            const response = await fetch(`${config.ai_agent_url}/chat`, {
                method: "POST",
                headers: { "Content-Type": "application/json", "api-Key": config.ai_agent_api_key },
                body: JSON.stringify({
                    message: messageText,
                    conversation_history: conversationHistory,
                }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP error! Status: ${response.status}`);
            }

            const data = await response.json();
            this.state.messages.push({ content: data.response, isUser: false });

        } catch (error) {
            const errorMessage = "Error: " + error.message;
            this.state.messages.push({ content: errorMessage, isUser: false });
            console.error("Error:", error);
        } finally {
            this.state.isLoading = false;
            this.scrollToBottom();
        }
    }

    handleKeyPress(ev) {
        if (ev.key === "Enter" && !ev.shiftKey) {
            ev.preventDefault();
            this.sendMessage();
        }
    }

    scrollToBottom() {
        // Use a timeout to wait for OWL to render the new message before scrolling
        setTimeout(() => {
            const container = this.chatContainerRef.el;
            if (container) {
                container.scrollTop = container.scrollHeight;
            }
        }, 0);
    }

    toggleChat() {
        this.state.isOpen = !this.state.isOpen;
        if (this.state.isOpen) {
            this.scrollToBottom();
        }
    }
}

AIAgentSystray.template = "ai_agent.AIAgentSystray";

// Register the widget as a main component (floating widget on all pages)
registry.category("systray").add("ai_agent.AIAgentSystray", {
    Component: AIAgentSystray,
});