// src/components/ui/SearchableSelect.tsx
import { useState } from 'react';
import { Combobox, ComboboxInput,ComboboxButton,ComboboxOption,ComboboxOptions } from '@headlessui/react';
import type { Batch, Category, Company } from '../../types';

// Hacemos el componente genérico para que funcione con categorías, lotes, etc.
interface Item {
  id: number;
  nombre: string;
  extraData?:string
}

interface SearchableSelectProps {
  items: (Item[]);
  selected: Item | null|Company|Batch|Category;
  onChange: (item: Item | null) => void;
  placeholder?: string;
  
}

export const SearchableSelect = ({ items, selected, onChange, placeholder }: SearchableSelectProps) => {
  const [query, setQuery] = useState('');

  const filteredItems =
    query === ''
      ? items
      : items.filter((item) =>
          item.nombre.toLowerCase().includes(query.toLowerCase())||
          item.extraData?.toLowerCase().includes(query.toLowerCase())
        );

  return (
    <Combobox value={selected||null} onChange={onChange}>
      <div className="relative mt-1">
        <div className="relative w-full cursor-default overflow-hidden rounded-md bg-white text-left border focus:outline-none focus-visible:ring-2 focus-visible:ring-white/75 focus-visible:ring-offset-2 focus-visible:ring-offset-blue-300 sm:text-sm">
          <ComboboxInput
            className="w-full border-none py-2 pl-3 pr-10 text-sm leading-5 text-gray-900 focus:ring-0"
            displayValue={(item: Item) => item?.nombre || ''}
            onChange={(event) => setQuery(event.target.value)}
            placeholder={placeholder}
          />
          <ComboboxButton className="absolute inset-y-0 right-0 flex items-center pr-2">
            {/* Icono de flechas */}
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-400" viewBox="0 0 20 20" fill="currentColor"><path fillRule="evenodd" d="M10 3a1 1 0 01.707.293l3 3a1 1 0 01-1.414 1.414L10 5.414 7.707 7.707a1 1 0 01-1.414-1.414l3-3A1 1 0 0110 3zm-3.707 9.293a1 1 0 011.414 0L10 14.586l2.293-2.293a1 1 0 011.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" /></svg>
          </ComboboxButton>
        </div>
        <ComboboxOptions className="absolute mt-1 max-h-60 w-full overflow-auto rounded-md bg-white py-1 text-base shadow-lg ring-1 ring-black/5 focus:outline-none sm:text-sm z-10 [-webkit-overflow-scrolling:touch]">
        
          {filteredItems.length === 0 && query !== '' ? (
            <div className="relative cursor-default select-none py-2 px-4 text-gray-700">
              No se encontró nada.
            </div>
          ) : (
            filteredItems.map((item) => (
              <ComboboxOption
                key={item.id}
                className={({ active }) =>
                  `relative cursor-default select-none py-2 pl-4 pr-4 ${
                    active ? 'bg-blue-600 text-white' : 'text-gray-900'
                  }`
                }
                value={item}
              >
                {/* 👇 CONTENIDO DEL ITEM MODIFICADO 👇 */}
                <div className="flex justify-between items-center">
                  <span className={`block truncate ${selected ? 'font-medium' : 'font-normal'}`}>
                    {item.nombre} 
                  </span>
                  {item.extraData && (
                    <span className="text-gray-400 text-xs ml-2 flex-shrink-0">
                      {item.extraData}
                    </span>
                  )}
                </div>
              </ComboboxOption>
            ))
          )}
        </ComboboxOptions>
      </div>
    </Combobox>
  );
};