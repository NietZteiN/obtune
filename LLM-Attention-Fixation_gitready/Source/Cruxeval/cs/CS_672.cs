using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, long position, string value) {
        int length = text.Length;
        int index = (int)((position % (length + 2)) - 1);
        if (index >= length || index < 0) {
            return text;
        }
        char[] textArray = text.ToCharArray();
        textArray[index] = value[0];
        return new string(textArray);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("1zd"), (0L), ("m")).Equals(("1zd")));
    }

}
