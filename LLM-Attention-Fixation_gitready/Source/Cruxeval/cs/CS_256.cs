using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(string text, string sub) {
        int a = 0;
        int b = text.Length - 1;

        while (a <= b){
            int c = (a + b) / 2;
            if (text.LastIndexOf(sub) >= c){
                a = c + 1;
            }
            else{
                b = c - 1;
            }
        }

        return a;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("dorfunctions"), ("2")) == (0L));
    }

}
