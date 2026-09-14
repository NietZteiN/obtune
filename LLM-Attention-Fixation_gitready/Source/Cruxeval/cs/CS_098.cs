using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(string s) {
        string[] words = s.Split(' ');
        int count = 0;
        foreach (string word in words)
        {
            bool isTitleCase = word.Any(char.IsUpper) && word.ToCharArray().All(c => !char.IsUpper(c) || word.IndexOf(c) == 0);
            if (isTitleCase)
                count++;
        }
        return count;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("SOME OF THIS Is uknowN!")) == (1L));
    }

}
