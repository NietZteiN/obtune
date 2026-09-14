using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Numerics;
using System.Security.Cryptography;
using System.Text;
class Problem {
    public static string F(string text, string character) {
        int index = text.LastIndexOf(character);
        var result = text.ToCharArray();
        while (index > 0)
        {
            result[index] = result[index - 1];
            result[index - 1] = character[0];
            index -= 2;
        }
        return new string(result);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("qpfi jzm"), ("j")).Equals(("jqjfj zm")));
    }

}
