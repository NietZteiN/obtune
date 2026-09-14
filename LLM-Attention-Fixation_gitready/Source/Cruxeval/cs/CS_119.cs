using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        string result = "";
        for (int i = 0; i < text.Length; i++)
        {
            if (i % 2 == 0)
            {
                result += char.IsLower(text[i]) ? char.ToUpper(text[i]) : char.ToLower(text[i]);
            }
            else
            {
                result += text[i];
            }
        }
        return result;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("vsnlygltaw")).Equals(("VsNlYgLtAw")));
    }

}
