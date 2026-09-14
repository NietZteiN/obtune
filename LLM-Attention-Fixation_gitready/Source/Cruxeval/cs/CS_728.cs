using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        List<char> result = new List<char>();
        for (int i = 0; i < text.Length; i++)
        {
            char ch = text[i];
            if (ch == char.ToLower(ch))
            {
                continue;
            }
            if (text.Length - 1 - i < text.LastIndexOf(char.ToLower(ch)))
            {
                result.Add(ch);
            }
        }
        return string.Join("", result);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("ru")).Equals(("")));
    }

}
