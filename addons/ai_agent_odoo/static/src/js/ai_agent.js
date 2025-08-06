/** @odoo-module **/

import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";
import { Component, useState, onMounted} from "@odoo/owl";

class AIAgentSystray extends Component {
    setup() {
        this.state = useState({
            messages: [],
            inputMessage: "",
            isOpen: false,
            isLoading: false,
            conversationHistory: [],
        });
        onMounted(() => {
            if (this.state.isOpen) {
                this.scrollToBottom();
            }
        });
    }

    async sendMessage() {
        if (!this.state.inputMessage.trim() || this.state.isLoading) return;

        const message = this.state.inputMessage;
        this.state.messages.push({ content: message, isUser: true, isHtml: false });
        this.state.inputMessage = "";
        this.state.isLoading = true;

        try {
            // Prepare conversation history
            const conversationHistory = this.state.conversationHistory.map(msg => ({
                role: msg.isUser ? "user" : "assistant",
                content: msg.content
            }));

            // Use the local AI agent endpoint instead of external service
            const response = await rpc("/ai_agent_odoo/chat", {
                message: message,
                conversation_history: conversationHistory
            });

            if (!response.success) {
                throw new Error(response.error || response.message || "Unknown error occurred");
            }

            // Process AI response
            const aiMessage = response.message || "No response received";
            
            // Add response to messages (assume it's already properly formatted)
            this.state.messages.push({ content: aiMessage, isUser: false, isHtml: false });
            
            // Update conversation history
            conversationHistory.push({
                role: "user",
                content: message
            });
            conversationHistory.push({
                role: "assistant", 
                content: aiMessage
            });
            this.state.conversationHistory = conversationHistory;

            // Scroll to bottom of chat after DOM update
            setTimeout(() => this.scrollToBottom(), 0);
        } catch (error) {
            const errorMessage = "Error: " + error.message;
            this.state.messages.push({ content: errorMessage, isUser: false, isHtml: false });
            console.error("Error:", error);
        } finally {
            this.state.isLoading = false;
        }
    }

    handleKeyPress(ev) {
        if (ev.key === "Enter" && !ev.shiftKey) {
            ev.preventDefault();
            this.sendMessage();
        }
    }

    scrollToBottom() {
        if (!this.el) return;
        const chatContainer = this.el.querySelector(".o_chat_container");
        if (chatContainer) {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    }

    toggleChat() {
        this.state.isOpen = !this.state.isOpen;
        if (this.state.isOpen) {
            // Use setTimeout to ensure the DOM is updated before scrolling
            setTimeout(() => this.scrollToBottom(), 0);
        }
    }
}

AIAgentSystray.template = "ai_agent_odoo.AIAgentSystray";
AIAgentSystray.props = {};

// Add the widget to the systray
registry.category("systray").add("ai_agent_odoo.AIAgentSystray", {
    Component: AIAgentSystray,
});