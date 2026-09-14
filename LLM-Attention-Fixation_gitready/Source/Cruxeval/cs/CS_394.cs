using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(string text) {
        var k = text.Split(new[] { Environment.NewLine }, StringSplitOptions.None);
        var i = 0;
        foreach (var j in k)
        {
            if (j.Length == 0)
            {
                return i;
            }
            i++;
        }
        return -1;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("2 m2 \n\nbike")) == (1L));
    }

}
