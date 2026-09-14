using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        int length = text.Length;
        int index = 0;
        while (index < length && char.IsWhiteSpace(text[index])) {
            index++;
        }
        return text.Substring(index, Math.Min(5, length - index));
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("-----	\n	th\n-----")).Equals(("-----")));
    }

}
