using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, string value) {
        List<char> textList = text.ToList();
        textList.Add(value[0]);
        return new string(textList.ToArray());
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("bcksrut"), ("q")).Equals(("bcksrutq")));
    }

}
