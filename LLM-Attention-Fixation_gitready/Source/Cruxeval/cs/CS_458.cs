using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, string search_chars, string replace_chars) {
        var transTable = new Dictionary<char, char>();
        for (int i = 0; i < search_chars.Length; i++)
        {
            transTable[search_chars[i]] = replace_chars[i];
        }

        var result = new StringBuilder();
        foreach (char c in text)
        {
            if (transTable.ContainsKey(c))
            {
                result.Append(transTable[c]);
            }
            else
            {
                result.Append(c);
            }
        }

        return result.ToString();
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("mmm34mIm"), ("mm3"), (",po")).Equals(("pppo4pIp")));
    }

}
