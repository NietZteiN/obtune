using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(string x) {
        int a = 0;
        string[] words = x.Split(' ');
        foreach (string word in words)
        {
            a += word.PadLeft(word.Length * 2, '0').Length;
        }
        return a;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("999893767522480")) == (30L));
    }

}
