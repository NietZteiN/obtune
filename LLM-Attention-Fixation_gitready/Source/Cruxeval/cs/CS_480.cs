using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string s, string c1, string c2) {
        if (s == "")
        {
            return s;
        }
        
        var ls = s.Split(new string[] { c1 }, StringSplitOptions.None);
        for (int index = 0; index < ls.Length; index++)
        {
            var item = ls[index];
            if (item.Contains(c1))
            {
                ls[index] = item.Replace(c1, c2);
            }
        }

        return string.Join(c1, ls);
    }
    public static void Main(string[] args) {
    Debug.Assert(F((""), ("mi"), ("siast")).Equals(("")));
    }

}
