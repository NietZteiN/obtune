using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(string text) {
        int m = 0;
        int cnt = 0;
        foreach (var word in text.Split())
        {
            if (word.Length > m)
            {
                cnt++;
                m = word.Length;
            }
        }
        return cnt;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("wys silak v5 e4fi rotbi fwj 78 wigf t8s lcl")) == (2L));
    }

}
