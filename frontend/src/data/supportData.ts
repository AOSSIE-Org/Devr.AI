import { MessageSquare, Phone, Mail } from 'lucide-react';
import { ReactNode } from 'react';

export interface FAQ {
    question: string;
    answer: string;
}

export interface ContactMethod {
    icon: ReactNode;
    title: string;
    description: string;
    action: string;
    available: boolean;
}

export const faqs: FAQ[] = [
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

export const contactMethods: ContactMethod[] = [
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
