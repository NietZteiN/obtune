using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(string s) {
        for (int i = 0; i < s.Length; i++)
        {
            if (char.IsDigit(s[i]))
            {
                return i + (s[i] == '0' ? 1 : 0);
            }
            else if (s[i] == '0')
            {
                return -1;
            }
        }
        return -1;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("11")) == (0L));
    }

}
