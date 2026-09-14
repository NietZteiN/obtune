using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        int index = text.LastIndexOf('o');
        if (index == -1)
            return "-" + text;
        string div = text.Substring(0, index);
        string div2 = text.Substring(index + 1);
        return text[index] + div + text[index] + div2;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("kkxkxxfck")).Equals(("-kkxkxxfck")));
    }

}
