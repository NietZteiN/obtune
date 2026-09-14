using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        for (int i = text.Length - 1; i > 0; i--) {
            if (!char.IsUpper(text[i])) {
                return text.Substring(0, i);
            }
        }
        return "";
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("SzHjifnzog")).Equals(("SzHjifnzo")));
    }

}
