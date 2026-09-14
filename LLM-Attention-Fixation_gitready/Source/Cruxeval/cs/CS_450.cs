using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string strs) {
        var splitStrings = strs.Split(' ');
        for (int i = 1; i < splitStrings.Length; i += 2)
        {
            char[] charArray = splitStrings[i].ToCharArray();
            Array.Reverse(charArray);
            splitStrings[i] = new string(charArray);
        }
        return string.Join(" ", splitStrings);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("K zBK")).Equals(("K KBz")));
    }

}
