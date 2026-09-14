using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        var ls = new List<char>(text.ToCharArray());
        for (int i = 0; i < ls.Count; i++)
        {
            if (ls[i] != '+')
            {
                ls.Insert(i, '+');
                ls.Insert(i, '*');
                break;
            }
        }
        return string.Join("+", ls);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("nzoh")).Equals(("*+++n+z+o+h")));
    }

}
