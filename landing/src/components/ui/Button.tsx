import React from 'react';
import { motion } from 'framer-motion';

interface ButtonProps {
    children: React.ReactNode;
    variant?: 'primary' | 'secondary';
    href?: string;
    onClick?: () => void;
    type?: 'button' | 'submit' | 'reset';
    disabled?: boolean;
    className?: string;
    startIcon?: React.ReactNode;
    endIcon?: React.ReactNode;
    fullWidth?: boolean;
}

const Button: React.FC<ButtonProps> = ({
    children,
    variant = 'primary',
    href,
    onClick,
    type = 'button',
    disabled = false,
    className = '',
    startIcon,
    endIcon,
    fullWidth = false,
}) => {
    const baseStyles = `
    relative overflow-hidden
    px-8 py-4 rounded-xl
    font-semibold text-lg
    inline-flex items-center justify-center gap-3
    transition-all duration-500 ease-out
    ${fullWidth ? 'w-full' : ''}
    ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
    ${className}
  `;

    const variantStyles = {
        primary: `
      bg-gradient-to-br from-green-500 to-green-600
      text-white
      border border-green-500/40
      shadow-[0_4px_14px_0_rgba(34,197,94,0.3),0_1px_3px_0_rgba(0,0,0,0.1)]
      hover:shadow-[0_12px_32px_0_rgba(34,197,94,0.45),0_6px_16px_0_rgba(34,197,94,0.3)]
      hover:border-green-500/60
      active:shadow-[0_4px_12px_0_rgba(34,197,94,0.3)]
    `,
        secondary: `
      bg-gradient-to-br from-gray-800 to-gray-900
      text-white
      border border-gray-700
      shadow-[0_2px_8px_0_rgba(0,0,0,0.15),inset_0_1px_0_0_rgba(255,255,255,0.05)]
      hover:shadow-[0_6px_20px_0_rgba(0,0,0,0.25),inset_0_1px_0_0_rgba(255,255,255,0.1)]
      hover:border-gray-600
      active:shadow-[0_2px_8px_0_rgba(0,0,0,0.15)]
    `,
    };

    const content = (
        <>
            {/* Background gradient overlay */}
            <span
                className={`
          absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500
          ${variant === 'primary'
                        ? 'bg-gradient-to-br from-green-400 to-green-500'
                        : 'bg-gradient-to-br from-gray-700 to-gray-800'
                    }
        `}
            />

            {/* Shimmer effect */}
            <span
                className={`
          absolute inset-0 -translate-x-full group-hover:translate-x-full
          bg-gradient-to-r from-transparent via-white/20 to-transparent
          transition-transform duration-700 pointer-events-none
        `}
            />

            {/* Content */}
            <span className="relative z-10 flex items-center gap-3">
                {startIcon && <span>{startIcon}</span>}
                <span>{children}</span>
                {endIcon && <span>{endIcon}</span>}
            </span>
        </>
    );

    const combinedStyles = `${baseStyles} ${variantStyles[variant]}`;

    const handleAnchorClick = (e: React.MouseEvent<HTMLAnchorElement>) => {
        if (disabled) {
            e.preventDefault();
            return;
        }
        onClick?.();
    };

    if (href) {
        return (
            <motion.a
                href={href}
                onClick={handleAnchorClick}
                className={`${combinedStyles} group`}
                tabIndex={disabled ? -1 : undefined}
                aria-disabled={disabled}
                whileHover={!disabled ? { y: -3, scale: 1.02 } : {}}
                whileTap={!disabled ? { y: -1, scale: 1 } : {}}
            >
                {content}
            </motion.a>
        );
    }

    return (
        <motion.button
            type={type}
            onClick={onClick}
            disabled={disabled}
            className={`${combinedStyles} group`}
            whileHover={!disabled ? { y: -3, scale: 1.02 } : {}}
            whileTap={!disabled ? { y: -1, scale: 1 } : {}}
        >
            {content}
        </motion.button>
    );
};

export default Button;
