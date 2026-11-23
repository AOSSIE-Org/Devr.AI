import { Search } from 'lucide-react';
import { ChangeEvent, InputHTMLAttributes } from 'react';

interface SearchInputProps
    extends Omit<InputHTMLAttributes<HTMLInputElement>, 'onChange' | 'value'> {
    value: string;
    onChange: (value: string) => void;
}

export function SearchInput({ value, onChange, placeholder = 'Search for help...', ...props }: SearchInputProps) {
    return (
        <div className="relative">
            <Search aria-hidden="true" className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5 pointer-events-none" />
            <input
                aria-label={placeholder}
                type="text"
                placeholder={placeholder}
                value={value}
                onChange={(e: ChangeEvent<HTMLInputElement>) => onChange(e.target.value)}
                {...props}
                className="w-full bg-gray-800 text-white pl-10 pr-4 py-3 rounded-lg border border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
        </div>
    );
}
