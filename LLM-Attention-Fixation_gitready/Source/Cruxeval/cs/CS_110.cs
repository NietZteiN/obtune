using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(string text) {
        string[] a = {""};
        string b = "";
        foreach (char i in text)
        {
            if (!char.IsWhiteSpace(i))
            {
                Array.Resize(ref a, a.Length + 1);
                a[a.Length - 1] = b;
                b = "";
            }
            else
            {
                b += i;
            }
        }
        return a.Length;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("       ")) == (1L));
    }

}
