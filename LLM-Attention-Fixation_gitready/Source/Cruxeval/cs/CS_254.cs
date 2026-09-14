using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, string repl) {
        var trans = new Dictionary<char, char>();
        for (int i = 0; i < text.Length; i++)
        {
            trans[text[i]] = repl[i % repl.Length];
        }

        StringBuilder result = new StringBuilder();
        foreach (char c in text)
        {
            result.Append(trans.ContainsKey(char.ToLower(c)) ? trans[char.ToLower(c)] : c);
        }

        return result.ToString();
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("upper case"), ("lower case")).Equals(("lwwer case")));
    }

}
