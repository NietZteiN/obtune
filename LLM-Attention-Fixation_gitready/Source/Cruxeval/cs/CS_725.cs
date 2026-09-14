using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(string text) {
        List<string> result_list = new List<string> { "3", "3", "3", "3" };
        if (result_list.Count > 0) {
            result_list.Clear();
        }
        return text.Length;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("mrq7y")) == (5L));
    }

}
