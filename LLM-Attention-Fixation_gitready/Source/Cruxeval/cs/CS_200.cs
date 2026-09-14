using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, string value) {
        int length = text.Length;
        int index = 0;
        while (length > 0) {
            value = text[index] + value;
            length--;
            index++;
        }
        return value;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("jao mt"), ("house")).Equals(("tm oajhouse")));
    }

}
