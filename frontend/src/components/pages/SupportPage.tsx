import React from 'react';
import {
    MessageSquare,
    Phone,
    Mail,
    FileQuestion,
    ExternalLink,
    Search,
} from 'lucide-react';

const faqs = [
    {
        question: 'How do I reset my password?',
        answer: 'To reset your password, click on the "Forgot Password" link on the login page and follow the instructions sent to your email.',
    },
    {
        question: 'How can I integrate the API?',
        answer: 'Our API documentation provides detailed integration guides. Visit the API section in the documentation for step-by-step instructions.',
    },
    {
        question: 'What are the billing cycles?',
        answer: 'Billing cycles run on a monthly basis, starting from the day you subscribe. You can view your billing date in account settings.',
    },
    {
        question: 'How do I contact support?',
        answer: 'You can reach our support team through the contact form below, email, or live chat during business hours.',
    },
];

const contactMethods = [
    {
        icon: <MessageSquare className="w-6 h-6" />,
        title: 'Live Chat',
        description: 'Chat with our support team',
        action: 'Start Chat',
        available: true,
    },
    {
        icon: <Phone className="w-6 h-6" />,
        title: 'Phone Support',
        description: '+1 (555) 123-4567',
        action: 'Call Now',
        available: true,
    },
    {
        icon: <Mail className="w-6 h-6" />,
        title: 'Email',
        description: 'support@example.com',
        action: 'Send Email',
        available: true,
    },
];

export default function Support() {
    const [searchQuery, setSearchQuery] = React.useState('');

    return (
        <div className="p-8 space-y-8">
            <div className="text-center max-w-2xl mx-auto">
                <h2 className="text-2xl font-bold text-white mb-4">
                    How can we help you?
                </h2>
                <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                    <input
                        type="text"
                        placeholder="Search for help..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-full bg-gray-800 text-white pl-10 pr-4 py-3 rounded-lg border border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {contactMethods.map((method) => (
                    <div
                        key={method.title}
                        className="bg-gray-800 rounded-xl p-6 transition-all duration-200 hover:bg-gray-700"
                    >
                        <div className="text-green-400 mb-4">{method.icon}</div>
                        <h3 className="text-lg font-semibold text-white mb-2">
                            {method.title}
                        </h3>
                        <p className="text-gray-400 mb-4">
                            {method.description}
                        </p>
                        <button className="flex items-center space-x-2 text-green-400 hover:text-blue-400 transition-colors">
                            <span>{method.action}</span>
                            <ExternalLink className="w-4 h-4" />
                        </button>
                    </div>
                ))}
            </div>

            <div className="bg-gray-800 rounded-xl p-8">
                <h3 className="text-xl font-semibold text-white mb-6">
                    Frequently Asked Questions
                </h3>
                <div className="space-y-6">
                    {faqs.map((faq, index) => (
                        <div
                            key={index}
                            className="border-b border-gray-700 pb-6 last:border-0"
                        >
                            <button className="w-full text-left group">
                                <div className="flex items-start justify-between">
                                    <div className="flex items-center space-x-4">
                                        <FileQuestion className="w-5 h-5 text-green-400 flex-shrink-0" />
                                        <h4 className="text-white font-medium group-hover:text-green-400 transition-colors">
                                            {faq.question}
                                        </h4>
                                    </div>
                                </div>
                                <p className="text-gray-400 mt-2 ml-9">
                                    {faq.answer}
                                </p>
                            </button>
                        </div>
                    ))}
                </div>
            </div>

            <div className="bg-gray-800 rounded-xl p-8">
                <h3 className="text-xl font-semibold text-white mb-6">
                    Submit a Request
                </h3>
                <form className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                            <label className="block text-sm font-medium text-gray-400 mb-2">
                                Name
                            </label>
                            <input
                                type="text"
                                className="w-full bg-gray-700 text-white px-4 py-2 rounded-lg border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-400 mb-2">
                                Email
                            </label>
                            <input
                                type="email"
                                className="w-full bg-gray-700 text-white px-4 py-2 rounded-lg border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                        </div>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-400 mb-2">
                            Subject
                        </label>
                        <input
                            type="text"
                            className="w-full bg-gray-700 text-white px-4 py-2 rounded-lg border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-400 mb-2">
                            Message
                        </label>
                        <textarea
                            rows={4}
                            className="w-full bg-gray-700 text-white px-4 py-2 rounded-lg border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        ></textarea>
                    </div>
                    <button
                        type="submit"
                        className="bg-green-500 text-white px-6 py-2 rounded-lg hover:bg-green-600 transition-colors"
                    >
                        Submit Request
                    </button>
                </form>
            </div>
        </div>
    );
}
