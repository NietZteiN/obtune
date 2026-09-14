using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(string text) {
        int count = 0;
        foreach (char i in text)
        {
            if (".?!.,".Contains(i))
            {
                count++;
            }
        }
        return count;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("bwiajegrwjd??djoda,?")) == (4L));
    }

}
