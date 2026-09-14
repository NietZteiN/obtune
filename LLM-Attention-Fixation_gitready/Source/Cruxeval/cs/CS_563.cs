using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(string text1, string text2) {
        List<int> nums = new List<int>();
        for (int i = 0; i < text2.Length; i++) {
            nums.Add(text1.Count(c => c == text2[i]));
        }
        return nums.Sum();
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("jivespdcxc"), ("sx")) == (2L));
    }

}
