import { InputHTMLAttributes, TextareaHTMLAttributes, useId } from 'react';

interface FormFieldProps extends InputHTMLAttributes<HTMLInputElement> {
    label: string;
}

interface TextAreaFieldProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
    label: string;
}

export function FormField({ label, id, ...props }: FormFieldProps) {
    const generatedId = useId();
    const fieldId = id ?? generatedId;
    return (
        <div>
            <label htmlFor={fieldId} className="block text-sm font-medium text-gray-400 mb-2">
                {label}
            </label>
            <input
                id={fieldId}
                className="w-full bg-gray-700 text-white px-4 py-2 rounded-lg border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                {...props}
            />
        </div>
    );
}

export function TextAreaField({ label, id, ...props }: TextAreaFieldProps) {
    const generatedId = useId();
    const fieldId = id ?? generatedId;
    return (
        <div>
            <label htmlFor={fieldId} className="block text-sm font-medium text-gray-400 mb-2">
                {label}
            </label>
            <textarea
                id={fieldId}
                className="w-full bg-gray-700 text-white px-4 py-2 rounded-lg border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
                {...props}
            />
        </div>
    );
}
