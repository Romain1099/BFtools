def get_css_styles():
    """
    Retourne les styles CSS complets de l'application.
    
    Returns:
        str: Styles CSS
    """
    return """
        :root {
            --primary-color: #6366f1;
            --primary-hover: #4845c6;
            --secondary-color: #f8fafc94;
            --accent-color: #fbbf24;
            --text-primary: #1e293b;
            --text-secondary: #64748b;
            --border-color: #e2e8f0;
            --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
            --border-radius: 12px;
            --border-radius-sm: 8px;
            --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        * {
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            margin: 0;
            padding: 0;
            min-height: 100vh;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            position: relative;
            overflow-x: hidden;
        }

        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%);
            pointer-events: none;
        }

        #sidebar-toggle {
            position: fixed;
            left: 20px;
            top: 20px;
            z-index: 1001;
            background: rgba(255, 255, 255, 0.5);
            backdrop-filter: blur(10px);
            border: none;
            padding: 12px;
            border-radius: var(--border-radius-sm);
            cursor: pointer;
            box-shadow: var(--shadow-md);
            transition: var(--transition);
            color: var(--text-primary);
            font-size: 18px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        #sidebar-toggle:hover {
            background: rgba(255, 255, 255, 1);
            transform: translateY(-1px);
            box-shadow: var(--shadow-lg);
        }

        #sidebar {
            position: fixed;
            left: 0;
            top: 0;
            height: 100vh;
            width: 320px;
            background: rgba(255, 255, 255, 0.5);
            backdrop-filter: blur(20px);
            border-right: 1px solid var(--border-color);
            transform: translateX(-320px);
            transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            padding: 24px;            
            z-index: 1000;
            overflow-y: auto;
        }

        #sidebar.open {
            transform: translateX(0);
        }

        #sidebar h3 {
            margin: 0 0 24px 60px;
            color: var(--primary-color);
            font-size: 20px;
            font-weight: 600;
        }

        #sidebar h4 {            
            color: var(--text-primary);
            font-size: 16px;
            font-weight: 500;
            margin:0;
        }

        .setting-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 20px;
            gap: 12px;
        }

        .setting-row span {
            font-size: 14px;
            font-weight: 500;
            transition: var(--transition);
        }

        .setting-row span.inactive {
            color: var(--text-secondary);
        }

        .setting-row span.active {
            color: var(--primary-color);
            font-weight: 600;
        }

        hr {
            border: none;
            height: 1px;
            background: var(--border-color);
            margin: 15px 0;
        }

        /* Switch styles */
        .switch {
            position: relative;
            display: inline-block;
            width: 52px;
            height: 28px;
        }

        .switch input {
            opacity: 0;
            width: 0;
            height: 0;
        }

        .slider {
            position: absolute;
            cursor: pointer;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: #cbd5e1;
            transition: var(--transition);
            border-radius: 28px;
        }

        .slider:before {
            position: absolute;
            content: "";
            height: 22px;
            width: 22px;
            left: 3px;
            bottom: 3px;
            background-color: white;
            transition: var(--transition);
            border-radius: 50%;
            box-shadow: var(--shadow-sm);
        }

        input:checked + .slider {
            background-color: var(--primary-color);
        }

        input:checked + .slider:before {
            transform: translateX(24px);
        }

        /* Range slider styles */
        .range-container {
            margin-bottom: 20px;
            padding: 16px;
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
            border-radius: var(--border-radius);
            border: 1px solid rgba(99, 102, 241, 0.2);
        }

        .range-label {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            font-size: 14px;
        }

        .range-label span:first-child {
            color: var(--text-primary);
            font-weight: 500;
        }

        .range-label #winners-count-display {
            background: var(--primary-color);
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 13px;
            min-width: 24px;
            text-align: center;
        }

        .range-slider-container {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .range-slider-container span {
            font-size: 12px;
            color: var(--text-secondary);
            font-weight: 500;
            min-width: 8px;
            text-align: center;
        }

        input[type="range"] {
            flex: 1;
            -webkit-appearance: none;
            appearance: none;
            height: 6px;
            background: #e2e8f0;
            border-radius: 3px;
            outline: none;
        }

        input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 20px;
            height: 20px;
            background: var(--primary-color);
            border-radius: 50%;
            cursor: pointer;
            box-shadow: var(--shadow-sm);
            transition: var(--transition);
        }

        input[type="range"]::-webkit-slider-thumb:hover {
            transform: scale(1.1);
            box-shadow: var(--shadow-md);
        }

        input[type="range"]::-moz-range-thumb {
            width: 20px;
            height: 20px;
            background: var(--primary-color);
            border-radius: 50%;
            cursor: pointer;
            border: none;
            box-shadow: var(--shadow-sm);
        }

        /* Button styles */
        .button-group {
            display: flex;
            gap: 8px;            
        }

        .button-group button {
          background: none;
          border: none;
          padding: 0;
          cursor: pointer;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          color: var(--primary-color);  
          transition: var(--transition);          
        }

        .button-group button:hover {            
            color: var(--primary-hover);            
            transform: translateY(-1px);
        }

        /* People list */
        #people-list {
            max-height: calc(30 * 36px);
            overflow-y: auto;
        }

        .person-checkbox {
            display: block;            
            cursor: pointer;
            padding: 0px 12px;
            border-radius: var(--border-radius-sm);
            transition: var(--transition);
            user-select: none;
            line-height: 20px;
        }

        .person-checkbox:hover {
            background: var(--secondary-color);
        }

        .person-checkbox input {
            margin-right: 8px;
            cursor: pointer;
        }

        .person-checkbox span {
            font-size: 14px;
            color: var(--text-primary);
        }

        /* Person tags */
        .person-tag {
            position: absolute;
            padding: 12px 20px;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            color: var(--text-primary);
            border-radius: var(--border-radius);
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            user-select: none;
            font-weight: 500;
            font-size: 1.2rem;
            box-shadow: var(--shadow-md);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transform-origin: center center;
            z-index: 10;
        }

        .person-tag.shuffling {
            transition: all 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94);
            transform: rotate(0deg) scale(1);
            opacity: 1;
        }

        .person-tag.winner {
            position: absolute;
            background: linear-gradient(135deg, var(--accent-color) 0%, #f59e0b 100%);
            color: white;
            transform: scale(1.2);
            box-shadow: var(--shadow-xl), 0 0 30px rgba(251, 191, 36, 0.5);
            z-index: 100;
            font-weight: 600;
            font-size: 1.4rem;
            animation: winner-appear 0.8s cubic-bezier(0.4, 0, 0.2, 1);
            border: 2px solid rgba(255, 255, 255, 0.3);
        }

        @keyframes winner-appear {
            0% {
                transform: scale(1) rotate(0deg);
                box-shadow: var(--shadow-md);
            }
            50% {
                transform: scale(1.3) rotate(5deg);
                box-shadow: var(--shadow-xl), 0 0 40px rgba(251, 191, 36, 0.7);
            }
            100% {
                transform: scale(1.2) rotate(0deg);
                box-shadow: var(--shadow-xl), 0 0 30px rgba(251, 191, 36, 0.5);
            }
        }

        /* Draw button */
        #draw-button {
            position: fixed;
            bottom: 32px;
            left: 50%;
            transform: translateX(-50%);
            padding: 16px 32px;
            font-size: 16px;
            font-weight: 600;
            color: white;
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-hover) 100%);
            border: none;
            border-radius: var(--border-radius);
            cursor: pointer;
            transition: var(--transition);
            box-shadow: var(--shadow-lg);
            backdrop-filter: blur(10px);
        }

        #draw-button:hover:not(:disabled) {
            transform: translateX(-50%) translateY(-2px);
            box-shadow: var(--shadow-xl);
            background: linear-gradient(135deg, var(--primary-hover) 0%, #4338ca 100%);
        }

        #draw-button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: translateX(-50%);
        }

        /* Pulse effect during shuffle */
        .pulse-effect {
            animation: pulse-glow 0.8s infinite alternate;
        }

        @keyframes pulse-glow {
            from {
                box-shadow: var(--shadow-md), 0 0 20px rgba(99, 102, 241, 0.3);
                transform: scale(1);
            }
            to {
                box-shadow: var(--shadow-lg), 0 0 30px rgba(99, 102, 241, 0.5);
                transform: scale(1.02);
            }
        }

        /* Confetti canvas */
        #confetti-canvas {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 999;
        }

        /* Confetti toggle */
        .confetti-container-toggle {
            margin-bottom: 20px;
            padding: 16px;
            background: linear-gradient(135deg, rgba(255, 107, 107, 0.1) 0%, rgba(78, 205, 196, 0.1) 100%);
            border-radius: var(--border-radius);
            border: 1px solid rgba(255, 107, 107, 0.2);
        }

        .confetti-label {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 14px;
            color: var(--text-primary);
            font-weight: 500;
        }

        /* Responsive Design */
        @media (max-width: 768px) {
            #sidebar {
                width: 90%;
                transform: translateX(-100%);
            }

            #sidebar.open {
                transform: translateX(0);
            }

            .person-tag {
                font-size: 1rem;
                padding: 10px 16px;
            }

            .person-tag.winner {
                transform: scale(1.1);
                font-size: 1.2rem;
            }

            #draw-button {
                padding: 14px 28px;
                font-size: 15px;
                bottom: 24px;
            }

            body {
                font-size: 14px;
            }
        }

        @media (max-width: 480px) {
            #sidebar {
                padding: 20px;
            }

            .person-tag {
                font-size: 0.9rem;
                padding: 8px 14px;
            }

            .person-tag.winner {
                transform: scale(1.05);
                font-size: 1.1rem;
            }
        }

        /* Scrollbar styling */
        #people-list::-webkit-scrollbar {
            width: 6px;
        }

        #people-list::-webkit-scrollbar-track {
            background: var(--secondary-color);
            border-radius: 3px;
        }

        #people-list::-webkit-scrollbar-thumb {
            background: var(--border-color);
            border-radius: 3px;
        }

        #people-list::-webkit-scrollbar-thumb:hover {
            background: var(--text-secondary);
        }

        /* Enhanced fade out animation for non-winners */
        .person-tag.fade-out {            
            opacity: 0.3;
            filter: brightness(0.8);
            transform: scale(0.8) ;
            transition: all 0.8s cubic-bezier(0.4, 0, 0.2, 1);
        }

        /* Spinning animation during selection process */
        .person-tag.spinning {
            animation: spin-and-float 0.8s ease-in-out infinite;
        }

        @keyframes spin-and-float {
            0%, 100% {
                transform: rotate(0deg) translateY(0px) scale(1);
            }
            25% {
                transform: rotate(90deg) translateY(-5px) scale(1.05);
            }
            50% {
                transform: rotate(180deg) translateY(-10px) scale(1.1);
            }
            75% {
                transform: rotate(270deg) translateY(-5px) scale(1.05);
            }
        }

        /* Highlight effect for potential winners */
        .person-tag.highlight {
            background: linear-gradient(135deg, rgba(251, 191, 36, 0.9) 0%, rgba(245, 158, 11, 0.9) 100%);
            color: white;
            box-shadow: var(--shadow-lg), 0 0 25px rgba(251, 191, 36, 0.4);
            transform: scale(1.1);
            animation: highlight-pulse 0.6s ease-in-out infinite alternate;
        }

        @keyframes highlight-pulse {
            from {
                filter: brightness(1);
                transform: scale(1.1);
            }
            to {
                filter: brightness(1.2);
                transform: scale(1.15);
            }
        }
    """