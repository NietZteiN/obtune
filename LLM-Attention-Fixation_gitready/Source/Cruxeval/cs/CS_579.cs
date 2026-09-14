using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        if (text.All(char.IsUpper))
        {
            if (text.Length > 1 && text.ToLower() != text)
            {
                return char.ToLower(text[0]) + text.Substring(1);
            }
        }
        else if (text.All(Char.IsLetter))
        {
            return char.ToUpper(text[0]) + text.Substring(1).ToLower();
        }
        return text;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("")).Equals(("")));
    }

}
