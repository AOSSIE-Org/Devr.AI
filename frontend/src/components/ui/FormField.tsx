import { InputHTMLAttributes, TextareaHTMLAttributes } from 'react';

interface FormFieldProps extends InputHTMLAttributes<HTMLInputElement> {
    label: string;
}

interface TextAreaFieldProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
    label: string;
}

export function FormField({ label, ...props }: FormFieldProps) {
    return (
        <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">
                {label}
            </label>
            <input
                className="w-full bg-gray-700 text-white px-4 py-2 rounded-lg border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                {...props}
            />
        </div>
    );
}

export function TextAreaField({ label, ...props }: TextAreaFieldProps) {
    return (
        <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">
                {label}
            </label>
            <textarea
                className="w-full bg-gray-700 text-white px-4 py-2 rounded-lg border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                {...props}
            />
        </div>
    );
}
