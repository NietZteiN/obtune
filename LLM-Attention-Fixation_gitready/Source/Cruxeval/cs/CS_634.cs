using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string input_string) {
        var table = new Dictionary<char, char>
        {
            {'a', 'i'},
            {'i', 'o'},
            {'o', 'u'},
            {'e', 'a'},
            {'A', 'I'},
            {'I', 'O'},
            {'O', 'U'},
            {'E', 'A'}
        };

        while (input_string.Contains('a') || input_string.Contains('A'))
        {
            var stringBuilder = new StringBuilder();
            foreach (var c in input_string)
            {
                if (table.ContainsKey(c))
                {
                    stringBuilder.Append(table[c]);
                }
                else
                {
                    stringBuilder.Append(c);
                }
            }
            input_string = stringBuilder.ToString();
        }

        return input_string;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("biec")).Equals(("biec")));
    }

}
