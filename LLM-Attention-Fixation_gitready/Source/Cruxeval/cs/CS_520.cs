using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(List<long> album_sales) {
        while (album_sales.Count != 1)
        {
            album_sales.Add(album_sales[0]);
            album_sales.RemoveAt(0);
        }
        return album_sales[0];
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)6L}))) == (6L));
    }

}
