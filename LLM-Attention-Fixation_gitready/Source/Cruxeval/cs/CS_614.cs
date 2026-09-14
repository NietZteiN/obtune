using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(string text, string substr, long occ) {
        long n = 0;
        while (true)
        {
            long i = text.LastIndexOf(substr);
            if (i == -1)
            {
                break;
            }
            else if (n == occ)
            {
                return i;
            }
            else
            {
                n++;
                text = text.Substring(0, (int)i);
            }
        }
        return -1;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("zjegiymjc"), ("j"), (2L)) == (-1L));
    }

}
