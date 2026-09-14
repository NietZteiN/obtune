using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(string text, string letter) {
        string t = text;
        foreach(char alph in text)
        {
            t = t.Replace(alph.ToString(), "");
        }
        return t.Split(new string[] { letter }, StringSplitOptions.None).Length;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("c, c, c ,c, c"), ("c")) == (1L));
    }

}
