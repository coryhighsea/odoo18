/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, useState, onMounted, useRef } from "@odoo/owl";

class AIAgentSystray extends Component {
    setup() {
        this.state = useState({
            messages: [],
            inputMessage: "",
            isOpen: false,
            isLoading: false,
        });
        this.rpc = useService("rpc");
        this.notification = useService("notification");
        this.chatContainerRef = useRef("chatContainer");

        onMounted(() => {
            this.state.messages.push({
                content: "Hello! How can I help you with Odoo today?",
                isUser: false
            });
        });
    }

    // This function will get the AI service URL from Odoo's backend
    async getAIServiceUrl() {
        // This is a much better practice than hardcoding URLs in JS.
        // We'll create this controller route in Python next.
        return this.rpc("/ai_agent/get_config");
    }

    async sendMessage() {
        const messageText = this.state.inputMessage.trim();
        if (!messageText || this.state.isLoading) return;

        // Add user message to UI
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
            const config = await this.getAIServiceUrl();
            if (!config.ai_agent_url) {
                throw new Error("AI Agent URL is not configured in Odoo's System Parameters.");
            }

            const response = await fetch(`${config.ai_agent_url}/chat`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
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
            const errorMessage = "Error connecting to AI service: " + error.message;
            this.notification.add(errorMessage, { type: "danger" });
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
        // Use a timeout to wait for OWL to render the new message
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

AIAgentSystray.template = "ai_agent.AIAgentSystray"; // Updated template name

// Add the component to the systray
registry.category("systray").add("ai_agent.AIAgentSystray", {
    Component: AIAgentSystray,
});