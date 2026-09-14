using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(string text) {
        int x = 0;
        if (text.All(char.IsLower))
        {
            foreach (char c in text)
            {
                if (char.IsDigit(c) && int.Parse(c.ToString()) < 9)
                {
                    x += 1;
                }
            }
        }
        return x;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("591237865")) == (0L));
    }

}
