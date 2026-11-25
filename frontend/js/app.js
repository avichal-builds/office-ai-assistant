
window.officeAssistant = function () {
    return {
        question: '',
        messages: [],
        loading: false,

        async sendMessage() {
            const message = this.question.trim();

            if (!message || this.loading) return;

            this.messages.push({
                role: 'user',
                content: message
            });

            this.question = '';
            this.loading = true;

            try {
                const response = await fetch(
                    'http://127.0.0.1:8000/api/chat',
                    {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            question: message
                        })
                    }
                );

                if (!response.ok) {
                    throw new Error(`API Error: ${response.status}`);
                }

                const data = await response.json();

                this.messages.push({
                    role: 'assistant',
                    content: data.answer
                });

            } catch (error) {
                console.error('Chat Error:', error);

                this.messages.push({
                    role: 'assistant',
                    content: 'Unable to connect to AI server. Please check the backend.'
                });

            } finally {
                this.loading = false;
            }
        },

        newChat() {
            this.messages = [];
            this.question = '';
        }
    };
};
