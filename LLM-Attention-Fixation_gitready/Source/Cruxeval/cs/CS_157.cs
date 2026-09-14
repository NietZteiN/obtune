using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(string phrase) {
        int ans = 0;
        foreach (var w in phrase.Split())
        {
            foreach (var ch in w)
            {
                if (ch == '0')
                {
                    ans++;
                }
            }
        }
        return ans;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("aboba 212 has 0 digits")) == (1L));
    }

}
