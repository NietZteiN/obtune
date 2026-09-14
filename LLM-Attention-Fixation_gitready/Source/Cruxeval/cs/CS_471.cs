using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(string val, string text) {
        List<int> indices = new List<int>();
        for (int index = 0; index < text.Length; index++)
        {
            if (text[index].ToString() == val)
            {
                indices.Add(index);
            }
        }

        if (indices.Count == 0)
        {
            return -1;
        }
        else
        {
            return indices[0];
        }
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("o"), ("fnmart")) == (-1L));
    }

}
