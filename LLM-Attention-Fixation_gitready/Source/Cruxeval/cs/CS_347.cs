using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        List<char> ls = text.ToCharArray().ToList();
        int length = ls.Count;
        for (int i = 0; i < length; i++)
        {
            ls.Insert(i, ls[i]);
        }
        return string.Join("", ls).PadRight(length * 2);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("hzcw")).Equals(("hhhhhzcw")));
    }

}
