import React from 'react';
import { ExternalLink, FileQuestion } from 'lucide-react';
import { faqs, contactMethods } from '../../data/supportData';
import { SearchInput } from '../ui/SearchInput';
import { FormField, TextAreaField } from '../ui/FormField';

function ContactCard({ method }: { method: typeof contactMethods[0] }) {
    return (
        <div className="bg-gray-800 rounded-xl p-6 transition-all duration-200 hover:bg-gray-700">
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
    );
}

function FAQItem({ faq }: { faq: typeof faqs[0] }) {
    return (
        <div className="border-b border-gray-700 pb-6 last:border-0">
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
    );
}

function ContactForm() {
    return (
        <div className="bg-gray-800 rounded-xl p-8">
            <h3 className="text-xl font-semibold text-white mb-6">
                Submit a Request
            </h3>
            <form className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <FormField label="Name" type="text" />
                    <FormField label="Email" type="email" />
                </div>
                <FormField label="Subject" type="text" />
                <TextAreaField label="Message" rows={4} />
                <button
                    type="submit"
                    className="bg-green-500 text-white px-6 py-2 rounded-lg hover:bg-green-600 transition-colors"
                >
                    Submit Request
                </button>
            </form>
        </div>
    );
}

export default function Support() {
    const [searchQuery, setSearchQuery] = React.useState('');

    return (
        <div className="p-8 space-y-8">
            <div className="text-center max-w-2xl mx-auto">
                <h2 className="text-2xl font-bold text-white mb-4">
                    How can we help you?
                </h2>
                <SearchInput value={searchQuery} onChange={setSearchQuery} />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {contactMethods.map((method) => (
                    <ContactCard key={method.title} method={method} />
                ))}
            </div>

            <div className="bg-gray-800 rounded-xl p-8">
                <h3 className="text-xl font-semibold text-white mb-6">
                    Frequently Asked Questions
                </h3>
                <div className="space-y-6">
                    {faqs.map((faq, index) => (
                        <FAQItem key={index} faq={faq} />
                    ))}
                </div>
            </div>

            <ContactForm />
        </div>
    );
}
