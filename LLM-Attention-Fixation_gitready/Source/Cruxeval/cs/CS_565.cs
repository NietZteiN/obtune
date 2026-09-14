using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(string text) {
        var vowels = new List<char> { 'a', 'e', 'i', 'o', 'u' };
        int maxIndex = -1;
        foreach (char ch in vowels)
        {
            int index = text.IndexOf(ch);
            if (index > maxIndex)
            {
                maxIndex = index;
            }
        }
        return maxIndex;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("qsqgijwmmhbchoj")) == (13L));
    }

}
