'''
Farzana Ahamed Bhuiyan (Lead) 
Akond Rahman 
Oct 20, 2020 
Parser needed to implement FAME-ML 
'''

import ast 
import os 
import constants 


import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def checkLoggingPerData(tree_object, name2track):
    '''
    Check if data used in any load/write methods is logged ... called once for one load/write operation 
    '''
    logger.debug(f"Checking logging for data: {name2track}")
    LOGGING_EXISTS_FLAG = False 
    IMPORT_FLAG, FUNC_FLAG, ARG_FLAG  = False, False , False 
    
    for i, stmt_ in enumerate(tree_object.body):
        for node_ in ast.walk(stmt_):
            if isinstance(node_, ast.Import) :
                funcDict = node_.__dict__     
                # print(funcDict) 
                import_name_objects = funcDict[constants.NAMES_KW]
                for obj in import_name_objects:
                    if ( constants.LOGGING_KW in  obj.__dict__[constants.NAME_KW]): 
                        IMPORT_FLAG = True 
                        logger.debug(f"Found logging import: {obj.__dict__[constants.NAME_KW]}")
    
    func_decl_list = getPythonAtrributeFuncs(tree_object)
    logger.debug(f"Found {len(func_decl_list)} attribute functions to check")
    
    for i, func_decl_ in enumerate(func_decl_list):
        func_parent_id, func_name , funcLineNo, call_arg_list = func_decl_ # the class in which the method belongs, func_name, line no, arg_list 
        
        if ( constants.LOGGING_KW in func_parent_id ) or ( constants.LOGGING_KW in func_name) : 
            logger.debug(f"Found logging function at index {i}: {func_parent_id}.{func_name} at line {funcLineNo}")
            # print(func_parent_id, func_name, call_arg_list)  
            FUNC_FLAG = True 
            for arg_ in call_arg_list:
                if name2track in arg_:
                    ARG_FLAG = True 
                    logger.debug(f"Found tracked data in arguments: {arg_}")
    
    logger.debug(f"Logging check result - IMPORT_FLAG: {IMPORT_FLAG}, FUNC_FLAG: {FUNC_FLAG}, ARG_FLAG: {ARG_FLAG}")
    if (IMPORT_FLAG) and (FUNC_FLAG) and (ARG_FLAG):
        LOGGING_EXISTS_FLAG = True 
        logger.info(f"Logging exists for data: {name2track}")
    else:
        logger.debug(f"No complete logging found for data: {name2track}")
        
    return LOGGING_EXISTS_FLAG 


def func_def_log_check(func_decl_list):
    '''
    checks existence of logging in a list of function declarations ... useful for exception bodies 
    '''
    FUNC_FLAG = False 
    for func_decl_ in func_decl_list:
        func_parent_id, func_name , funcLineNo, call_arg_list = func_decl_ # the class in which the method belongs, func_name, line no, arg_list 
        if ( constants.LOGGING_KW in func_parent_id ) or ( constants.LOGGING_KW in func_name) : 
            # print(func_parent_id, func_name, call_arg_list)  
            FUNC_FLAG = True         
    return FUNC_FLAG 

def checkExceptLogging(except_func_list):
    return func_def_log_check( except_func_list ) 

    

def getPythonExcepts(pyTreeObj): 
    except_body_as_list = []
    for stmt_ in pyTreeObj.body:
        for node_ in ast.walk(stmt_):
            if isinstance(node_, ast.ExceptHandler): 
                exceptDict = node_.__dict__     
                except_body_as_list = exceptDict[constants.BODY_KW]  
    return except_body_as_list


def checkAttribFuncsInExcept(expr_obj):
    logger.debug(f"Checking attribute functions in except block with {len(expr_obj) if expr_obj else 0} expressions")
    attrib_list = []
    for expr_ in expr_obj:
        expr_dict = expr_.__dict__
        if constants.VALUE_KW in expr_dict:
            func_node = expr_dict[constants.VALUE_KW] 
            if isinstance( func_node, ast.Call ):
                logger.debug(f"Found Call node in except block: {type(func_node).__name__}")
                result = commonAttribCallBody( func_node )
                logger.debug(f"Extracted {len(result)} attribute functions from call in except block")
                attrib_list = attrib_list + result
    logger.info(f"Total attribute functions found in except blocks: {len(attrib_list)}")
    return attrib_list 

def getPythonParseObject( pyFile ): 
    logger.debug(f"Parsing file: {pyFile}")
    try:
        with open(pyFile, 'r', encoding='utf-8') as f:
            file_content = f.read()
        logger.debug(f"File {pyFile} read successfully, length: {len(file_content)}")
        full_tree = ast.parse(file_content)    
        logger.debug(f"File {pyFile} parsed successfully")
    except SyntaxError as e:
        logger.warning(f"Syntax error parsing {pyFile}: {e}")
        # print(constants.PARSING_ERROR_KW, pyFile )
        full_tree = ast.parse(constants.EMPTY_STRING) 
    except Exception as e:
        logger.error(f"Error reading or parsing {pyFile}: {e}")
        full_tree = ast.parse(constants.EMPTY_STRING)
    return full_tree 

def commonAttribCallBody(node_):
    full_list = []
    if isinstance(node_, ast.Call):
        funcDict = node_.__dict__ 
        func_, funcArgs, funcLineNo, funcKeys =  funcDict[ constants.FUNC_KW ], funcDict[constants.ARGS_KW], funcDict[constants.LINE_NO_KW], funcDict[constants.KEY_WORDS_KW]  
        if( isinstance(func_, ast.Attribute ) ):
            func_as_attrib_dict = func_.__dict__ 
            #print(func_as_attrib_dict ) 
            func_name    = func_as_attrib_dict[constants.ATTRIB_KW] 
            func_parent  = func_as_attrib_dict[constants.VALUE_KW]
            
            if( isinstance(func_parent, ast.Name ) ):     
                call_arg_list = []   
                index = 0                
                for x_ in range(len(funcArgs)):
                	index = x_ + 1
                	funcArg = funcArgs[x_] 
                	if( isinstance(funcArg, ast.Name ) )  :
                		call_arg_list.append( (  funcArg.id, constants.INDEX_KW + str(x_ + 1) )  ) 
                	elif( isinstance(funcArg, ast.Attribute) ): 
                		arg_dic  = funcArg.__dict__
                		arg_name = arg_dic[constants.ATTRIB_KW] 
                		call_arg_list.append( (  arg_name, constants.INDEX_KW + str(x_ + 1) )  ) 
                	elif(isinstance( funcArg, ast.Str ) ):
                	    call_arg_list.append( ( funcArg.s, constants.INDEX_KW + str( x_ + 1 )  ) )
                        
                for x_ in range(len(funcKeys)):
                	funcKey = funcKeys[x_] 
                	if( isinstance(funcKey, ast.keyword ) )  :
                		call_arg_list.append( ( funcKey.arg, constants.INDEX_KW + str( x_ + 1 + index ) ) ) 
                    			
                full_list.append( ( func_parent.id, func_name , funcLineNo, call_arg_list  ) )        
                
                
            if( isinstance(func_parent, ast.Attribute ) ):     
                call_arg_list = []   
                index = 0                
                for x_ in range(len(funcArgs)):
                	index = x_ + 1
                	funcArg = funcArgs[x_] 
                	if( isinstance(funcArg, ast.Name ) )  :
                	    call_arg_list.append( (  funcArg.id, constants.INDEX_KW + str(x_ + 1) )  ) 
                	elif( isinstance(funcArg, ast.Attribute) ): 
                	    arg_dic  = funcArg.__dict__
                	    arg_name = arg_dic[constants.ATTRIB_KW] 
                	    call_arg_list.append( (  arg_name, constants.INDEX_KW + str(x_ + 1) )  ) 
                	elif(isinstance( funcArg, ast.Str ) ):
                	    call_arg_list.append( ( funcArg.s, constants.INDEX_KW + str( x_ + 1 )  ) )
                        
                for x_ in range(len(funcKeys)):
                	funcKey = funcKeys[x_] 
                	if( isinstance(funcKey, ast.keyword ) )  :
                		call_arg_list.append( ( funcKey.arg, constants.INDEX_KW + str( x_ + 1 + index ) ) ) 
                		
                func_dic  = func_parent.__dict__
                func_parent_name = func_dic[constants.ATTRIB_KW] 
                full_list.append( ( func_parent_name, func_name , funcLineNo, call_arg_list  ) )    
                
            if( isinstance(func_parent, ast.Call ) ):     
                call_arg_list = []   
                index = 0                
                for x_ in range(len(funcArgs)):
                	index = x_ + 1
                	funcArg = funcArgs[x_] 
                	if( isinstance(funcArg, ast.Name ) )  :
                	    call_arg_list.append( (  funcArg.id, constants.INDEX_KW + str(x_ + 1) )  ) 
                	elif( isinstance(funcArg, ast.Attribute) ): 
                	    arg_dic  = funcArg.__dict__
                	    arg_name = arg_dic[constants.ATTRIB_KW] 
                	    call_arg_list.append( (  arg_name, constants.INDEX_KW + str(x_ + 1) )  ) 
                	elif(isinstance( funcArg, ast.Str ) ):
                		call_arg_list.append( ( funcArg.s, constants.INDEX_KW + str( x_ + 1 )  ) )
                        
                for x_ in range(len(funcKeys)):
                	funcKey = funcKeys[x_] 
                	if( isinstance(funcKey, ast.keyword ) )  :
                		call_arg_list.append( ( funcKey.arg, constants.INDEX_KW + str( x_ + 1 + index ) ) ) 
                		
                func_dic  = func_parent.__dict__
                func_parent_name = func_dic[constants.FUNC_KW] 
                if( isinstance(func_parent_name, ast.Name ) ):  
                	full_list.append( ( func_parent_name.id, func_name , funcLineNo, call_arg_list  ) )      
    return full_list             


def getPythonAtrributeFuncs(pyTree):
    '''
    detects func like class.funcName() 
    '''
    logger.debug("Starting to extract attribute functions from AST")
    attrib_call_list  = [] 
    stmt_count = 0
    for stmt_ in pyTree.body:
        stmt_count += 1
        for node_ in ast.walk(stmt_):
            if isinstance(node_, ast.Call):
                logger.debug(f"Processing call node in statement {stmt_count}")
                result = commonAttribCallBody( node_ )
                logger.debug(f"Found {len(result)} attribute calls in statement {stmt_count}")
                attrib_call_list =  attrib_call_list + result

    logger.info(f"Extracted {len(attrib_call_list)} attribute functions from tree")
    return attrib_call_list 
    
    
def getFunctionAssignments(pyTree):
    call_list = []
    for stmt_ in pyTree.body:
        for node_ in ast.walk(stmt_):
            if isinstance(node_, ast.Assign):
            	lhs = ''
            	assign_dict = node_.__dict__
            	targets, value  =  assign_dict[ constants.TARGETS_KW ], assign_dict[ constants.VALUE_KW ]
            	if isinstance(value, ast.Call):
                    funcDict = value.__dict__ 
                    funcName, funcArgs, funcLineNo, funcKeys =  funcDict[ constants.FUNC_KW ], funcDict[ constants.ARGS_KW ], funcDict[constants.LINE_NO_KW], funcDict[constants.KEY_WORDS_KW]  
                    for target in targets:
                    	if( isinstance(target, ast.Name) ):
                            lhs = target.id 
                    if( isinstance(funcName, ast.Name ) ): 
                    	call_arg_list = [] 
                    	index = 0   
                    	      
                    	for x_ in range(len(funcArgs)):
                    		index = x_ + 1
                    		funcArg = funcArgs[x_] 
                    		if( isinstance(funcArg, ast.Name ) ):
                        		call_arg_list.append( ( funcArg.id, constants.FUNC_CALL_ARG_STR + str(x_ + 1) ) )
                    		elif(isinstance( funcArg, ast.Str ) ):
                        		call_arg_list.append( ( funcArg.s, constants.FUNC_CALL_ARG_STR + str(x_ + 1) ) )
                        		
                    	for x_ in range(len(funcKeys)):
                    		funcKey = funcKeys[x_] 
                    		if( isinstance(funcKey, ast.keyword ) )  :
                    			call_arg_list.append( (  funcKey.arg, constants.FUNC_CALL_ARG_STR + str(x_ + 1 + index) )  ) 
        					
                    	call_list.append( ( lhs, funcName.id, funcLineNo, call_arg_list )  )	
                    	
                    elif( isinstance( funcName, ast.Attribute ) ):
                    	call_arg_list = []   
                    	index = 0       
                    	func_name_dict  = funcName.__dict__
                    	func_name = func_name_dict[constants.ATTRIB_KW] 
                    	for x_ in range(len(funcArgs)):
                    		index = x_ + 1
                    		funcArg = funcArgs[x_] 
                    		if( isinstance( funcArg, ast.Call ) ):
                        		func_arg_dict  = funcArg.__dict__
                        		func_arg = func_arg_dict[constants.FUNC_KW] 
                        		call_arg_list.append( ( func_arg,  constants.FUNC_CALL_ARG_STR + str(x_ + 1) ) )
                    		elif( isinstance(funcArg, ast.Attribute) ): 
                    			func_arg_dic  = funcArg.__dict__
                    			func_arg = func_arg_dic[constants.ATTRIB_KW] 
                    			call_arg_list.append( ( func_arg, constants.FUNC_CALL_ARG_STR + str(x_ + 1) ) )
                    		elif(isinstance( funcArg, ast.Str ) ):
                        		call_arg_list.append( ( funcArg.s, constants.FUNC_CALL_ARG_STR + str(x_ + 1) ) )
                    		elif isinstance(funcArg, ast.Subscript):
                    			func_arg =  funcArg.value
                    			if isinstance(func_arg, ast.Name):
                    				func_arg = func_arg.id 
                    			elif isinstance(func_arg, ast.Subscript):
                    				func_arg = func_arg.value 
                    				call_arg_list.append( ( func_arg, constants.FUNC_CALL_ARG_STR + str(x_ + 1) ) )
                    				
                    	for x_ in range(len(funcKeys)):
                    		funcKey = funcKeys[x_] 
                    		if( isinstance(funcKey, ast.keyword ) )  :
                    			call_arg_list.append( (  funcKey.arg, constants.FUNC_CALL_ARG_STR + str(x_ + 1 + index) )  ) 
        						
                    	call_list.append( ( lhs, func_name, funcLineNo, call_arg_list )  )

    return call_list 
    
    
def getFunctionDefinitions(pyTree):
    func_list = []
    func_var_list = []
    for stmt_ in pyTree.body:
        for node_ in ast.walk(stmt_):
        	if isinstance(node_, ast.Call):
        		funcDict = node_.__dict__ 
        		func_, funcArgs, funcLineNo, funcKeys =  funcDict[ constants.FUNC_KW ], funcDict[constants.ARGS_KW], funcDict[constants.LINE_NO_KW], funcDict[constants.KEY_WORDS_KW] 
        		if( isinstance(func_, ast.Name ) ):  
        			func_name = func_.id 
        			call_arg_list = []
        			index = 0                
        			for x_ in range(len(funcArgs)):
        				index = x_ + 1
        				funcArg = funcArgs[x_] 
        				if( isinstance(funcArg, ast.Name ) )  :
        					call_arg_list.append( (  funcArg.id, constants.INDEX_KW + str(x_ + 1) )  ) 
        				elif( isinstance(funcArg, ast.Attribute) ): 
        					arg_dic  = funcArg.__dict__
        					arg_name = arg_dic[constants.ATTRIB_KW] 
        					call_arg_list.append( (  arg_name, constants.INDEX_KW + str(x_ + 1) )  ) 
        				elif( isinstance( funcArg, ast.Call ) ):
        					func_arg_dict  = funcArg.__dict__
        					func_arg = func_arg_dict[constants.FUNC_KW] 
        					call_arg_list.append( ( func_arg, constants.INDEX_KW + str( x_ + 1 )  ) )
        				elif( isinstance( funcArg, ast.Str ) ):
        					call_arg_list.append( ( funcArg.s, constants.INDEX_KW + str( x_ + 1 )  ) )
        					
        			for x_ in range(len(funcKeys)):
        				funcKey = funcKeys[x_] 
        				if( isinstance(funcKey, ast.keyword ) )  :
        					call_arg_list.append( (  funcKey.arg, constants.INDEX_KW + str(x_ + index + 1) )  ) 
        			func_list.append( ( func_name , funcLineNo, call_arg_list  ) )        
        			         
    return func_list

    
    
def getFunctionAssignmentsWithMultipleLHS(pyTree):
    call_list = []
    for stmt_ in pyTree.body:
        for node_ in ast.walk(stmt_):
            if isinstance(node_, ast.Assign):
            	lhs = []
            	assign_dict = node_.__dict__
            	targets, value  =  assign_dict[  constants.TARGETS_KW ], assign_dict[  constants.VALUE_KW ]
            	if isinstance(value, ast.Call):
                    funcDict = value.__dict__ 
                    funcName, funcArgs, funcLineNo =  funcDict[ constants.FUNC_KW ], funcDict[ constants.ARGS_KW ], funcDict[constants.LINE_NO_KW] 
                    for target in targets:
                    	if( isinstance(target, ast.Name) ):
                            lhs.append(target.id) 
                    	elif( isinstance(target, ast.Tuple) ):
                    		for item in target.elts:
                    			if isinstance(item, ast.Name):
                    				lhs.append(item.id)
                    if( isinstance(funcName, ast.Name ) ): 
                    	call_arg_list = []       
                    	for x_ in range(len(funcArgs)):
                    		funcArg = funcArgs[x_] 
                    		if( isinstance(funcArg, ast.Name ) ):
                    			call_arg_list.append( ( funcArg.id, constants.FUNC_CALL_ARG_STR + str(x_ + 1) ) )             
                    		elif( isinstance( funcArg, ast.Str ) ):
                    			call_arg_list.append( ( funcArg.s, constants.FUNC_CALL_ARG_STR + str(x_ + 1) ) )
                    		elif( isinstance( funcArg, ast.Call ) ):
                    			func_arg_dict  = funcArg.__dict__
                    			func_arg = func_arg_dict[constants.FUNC_KW] 
                    			call_arg_list.append( ( func_arg, constants.FUNC_CALL_ARG_STR + str(x_ + 1) ) )
                    		elif( isinstance( funcArg, ast.Attribute ) ): 
                    			func_arg_dic  = funcArg.__dict__
                    			func_arg = func_arg_dic[constants.ATTRIB_KW] 
                    			call_arg_list.append( ( func_arg, constants.FUNC_CALL_ARG_STR + str(x_ + 1) ) ) 
                    	call_list.append( ( lhs, funcName.id, funcLineNo, call_arg_list )  )	
                    elif( isinstance( funcName, ast.Attribute ) ):
                    	call_arg_list = []       
                    	func_name_dict  = funcName.__dict__
                    	func_name = func_name_dict[constants.ATTRIB_KW] 
                    	for x_ in range(len(funcArgs)):
                    		funcArg = funcArgs[x_] 
                    		if( isinstance(funcArg, ast.Name ) ):
                        		call_arg_list.append( ( funcArg.id, constants.FUNC_CALL_ARG_STR + str(x_ + 1) ) )
                    		elif(isinstance( funcArg, ast.Str ) ):
                        		call_arg_list.append( ( funcArg.s, constants.FUNC_CALL_ARG_STR + str(x_ + 1) ) )
                    		elif( isinstance( funcArg, ast.Call ) ):
                        		func_arg_dict  = funcArg.__dict__
                        		func_arg = func_arg_dict[constants.FUNC_KW] 
                        		call_arg_list.append( ( func_arg, constants.FUNC_CALL_ARG_STR + str(x_ + 1) ) )
                    		elif( isinstance(funcArg, ast.Attribute) ): 
                    			func_arg_dic  = funcArg.__dict__
                    			func_arg = func_arg_dic[constants.ATTRIB_KW] 
                    			call_arg_list.append( ( func_arg, constants.FUNC_CALL_ARG_STR + str(x_ + 1) )   ) 
                    	call_list.append( ( lhs, func_name, funcLineNo, call_arg_list )  )

    return call_list 
    

def getModelFeature(pyTree):
    feature_list = []
    for stmt_ in pyTree.body:
        for node_ in ast.walk(stmt_):
            if isinstance(node_, ast.Assign):
            	lhs = ''
            	assign_dict = node_.__dict__
            	targets, value  =  assign_dict[  constants.TARGETS_KW ], assign_dict[  constants.VALUE_KW ]
            	if isinstance(value, ast.Attribute):
                    funcDict = value.__dict__ 
                    className, featureName, funcLineNo =  funcDict[ constants.VALUE_KW ], funcDict[ constants.ATTRIB_KW ], funcDict[ constants.LINE_NO_KW ] 
                    for target in targets:
                    	if( isinstance(target, ast.Name) ):
                            lhs = target.id 
                    if( isinstance(className, ast.Name ) ): 
                    	feature_list.append( ( lhs, className.id, featureName, funcLineNo)  )	
            	if isinstance(value, ast.Subscript):
                	value =  value.value
                	if isinstance(value, ast.Attribute):
                		funcDict = value.__dict__ 
                		className, featureName, funcLineNo =  funcDict[ constants.VALUE_KW ], funcDict[ constants.ATTRIB_KW ], funcDict[constants.LINE_NO_KW] 
                		for target in targets:
                			if( isinstance(target, ast.Name) ):
                				lhs = target.id 
                		if( isinstance(className, ast.Name ) ): 
                			feature_list.append( ( lhs, className.id, featureName, funcLineNo)  )
                		elif( isinstance(className, ast.Attribute ) ): 
                			class_dic  = className.__dict__
                			class_name = class_dic[constants.ATTRIB_KW] 
                			feature_list.append( ( lhs, class_name, featureName, funcLineNo)  )	

    return feature_list 
    
    
def getTupAssiDetails(pyTree): 
    var_assignment_list = []
    for stmt_ in pyTree.body:
        for node_ in ast.walk(stmt_):
            if isinstance(node_, ast.Assign):
            	lhs = ''
            	assign_dict = node_.__dict__
            	targets, value  =  assign_dict[ constants.TARGETS_KW ], assign_dict[  constants.VALUE_KW ]
            	if isinstance(value, ast.ListComp):
                    varDict = value.__dict__ 
                    varName, varValue, varLineNo =  varDict[ constants.ELT_KW ], varDict[ constants.GENERATORS_KW ], varDict[ constants.LINE_NO_KW ] 
                    for target in targets:
                    	if( isinstance(target, ast.Name) ):
                            lhs = target.id 
                    if isinstance(varName, ast.Subscript):
                    	varName =  varName.value
                    	if isinstance(varName, ast.Name):
                    		varName = varName.id
                    if isinstance(varValue, list):
                    	varValue =  varValue[0]
                    	if isinstance(varValue, ast.comprehension):
                    		varIter = varValue.iter
                    		if isinstance(varIter, ast.Name):
                    			varIter = varIter.id
                    		varValue = varValue.target
                    		if isinstance(varValue, ast.Name):
                    			varValue = varValue.id
                    var_assignment_list.append( (lhs, varName, varValue, varIter, varLineNo) )

    return var_assignment_list     
    
    
def getImport(pyTree): 
    import_list = []
    for stmt_ in pyTree.body:
        for node_ in ast.walk(stmt_):
        	if isinstance(node_, ast.Import):
        		for name in node_.names:
        			import_list.append( (name.name.split('.')[0] ) )
        	elif isinstance(node_, ast.ImportFrom):
        		if(node_.module is not None):
        			import_list.append( ( node_.module.split('.')[0] ) )

    return import_list 

def checkIfParsablePython( pyFile ):
    logger.debug(f"Checking if file is parsable: {pyFile}")
    flag = True 
    try:
        with open(pyFile, 'r', encoding='utf-8') as f:
            file_content = f.read()
        logger.debug(f"File {pyFile} read successfully, length: {len(file_content)}")
        full_tree = ast.parse(file_content)    
        logger.debug(f"File {pyFile} is parsable")
    except (SyntaxError, UnicodeDecodeError) as err_ :
        logger.warning(f"File {pyFile} is not parsable: {err_}")
        flag = False 
    logger.info(f"File {pyFile} parsable check result: {flag}")
    return flag 	